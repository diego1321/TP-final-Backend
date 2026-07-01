from decimal import Decimal
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from ventas.models import Venta, DetalleVenta
from compras.models import Proveedor
from .models import Producto, Movimiento
from .forms import ProductoForm
from .services import InventarioService
from django.views.generic import DetailView
from ventas.forms import ClienteForm
from compras.forms import ProveedorForm


# 1. ESTO DEBE IR PRIMERO SIEMPRE (Para que las vistas de abajo lo puedan usar)
class AdminOrOperadorMixin(UserPassesTestMixin):
    """Controla que el usuario tenga permisos de escritura (Admin u Operador)."""
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name__in=['Admin', 'Operador']).exists()


# 2. VISTAS DEL DASHBOARD Y CATÁLOGO
class DashboardView(LoginRequiredMixin, ListView):   
    """Vista principal del panel de control."""
    model = Producto
    template_name = 'inventario/dashboard.html' 
    context_object_name = 'productos'

    def get_queryset(self):
        return Producto.objects.filter(activo=True).order_by('nombre')

    def get_context_data(self, **kwargs): #  Correcto
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['rol'] = 'Admin'
        else:
            grupo = self.request.user.groups.first()
            context['rol'] = grupo.name if grupo else 'Consulta'
            
        context['movimientos'] = InventarioService.obtener_historial_movimientos()
        context['form'] = ProductoForm()
        context['form_cliente'] = ClienteForm()
        context['form_proveedor'] = ProveedorForm()
        return context

class CrearProductoView(LoginRequiredMixin, AdminOrOperadorMixin, CreateView):
    """Alta de nuevos productos en el catálogo."""
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/dashboard.html'
    success_url = reverse_lazy('inventario:dashboard')

    def form_valid(self, form):
        producto = form.save(commit=False)
        stock_inicial = form.cleaned_data.get('cantidad_inicial') or 0
        producto.cantidad = 0
        producto.save()
        self.object = producto

        if stock_inicial > 0:
            try:
                InventarioService.registrar_movimiento_stock(
                    producto_id=producto.id,
                    tipo='ENTRADA',
                    cantidad=stock_inicial,
                    usuario=self.request.user
                )
            except Exception as e:
                messages.error(self.request, f"Producto creado, pero hubo un error con el stock: {str(e)}")
                return HttpResponseRedirect(self.get_success_url())

        messages.success(self.request, "Producto creado con éxito.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Error al crear el producto.")
        return redirect('inventario:dashboard')

class EditarProductoView(LoginRequiredMixin, AdminOrOperadorMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'inventario/editar_producto.html'
    success_url = reverse_lazy('inventario:dashboard')

    def form_valid(self, form):
        # NOTA: Aquí, si quieres usar tu servicio en lugar del .save() automático, 
        # deberías implementar la lógica que charlamos antes. 
        # Por ahora, esto cumple con tu código actual.
        messages.success(self.request, "Producto modificado con éxito.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Y aquí llamamos a super() con self
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_superuser:
            context['rol'] = 'Admin'
        else:
            grupo = self.request.user.groups.first()
            context['rol'] = grupo.name if grupo else 'Consulta'
            
        return context

class EliminarProductoView(LoginRequiredMixin, AdminOrOperadorMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        producto = get_object_or_404(Producto, id=pk)
        producto.activo = False
        producto.save()
        messages.success(request, f"Producto {producto.nombre} desactivado correctamente.")
        return redirect('inventario:dashboard')

class RegistrarMovimientoView(LoginRequiredMixin, AdminOrOperadorMixin, View):
    def post(self, request):
        producto_id = request.POST.get('producto_id')
        tipo = request.POST.get('tipo')
        cantidad = int(request.POST.get('cantidad', 0))
        try:
            InventarioService.registrar_movimiento_stock(
                producto_id=producto_id, tipo=tipo, cantidad=cantidad, usuario=request.user
            )
            messages.success(request, f"Movimiento de {tipo} registrado correctamente.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
        return redirect('inventario:dashboard')

class ExportarProductosCSVView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return InventarioService.generar_csv_productos()

class ExportarMovimientosCSVView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
            messages.error(request, "No tiene permisos.")
            return redirect('inventario:dashboard')
        return InventarioService.generar_csv_movimientos()

# --- VISTAS PARA LA SIMULACIÓN DE OPERACIONES (CORREGIDAS SIN INDEX OUT OF RANGE) ---
    

class ProductosMasVendidosView(LoginRequiredMixin, AdminOrOperadorMixin, ListView):
    model = Producto
    template_name = 'inventario/productos_mas_vendidos.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return InventarioService.obtener_productos_mas_vendidos(limite=10)