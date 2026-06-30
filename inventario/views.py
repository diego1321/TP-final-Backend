from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Producto, Movimiento, Compra, Venta, Proveedor, Cliente
from .forms import ProductoForm
from .services import InventarioService

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
    template_name = 'dashboard.html'
    context_object_name = 'productos'

    def get_queryset(self):
        return InventarioService.obtener_todos_los_productos()

    def get_context_data(self, **kwargs): #  Correcto
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['rol'] = 'Admin'
        else:
            grupo = self.request.user.groups.first()
            context['rol'] = grupo.name if grupo else 'Consulta'
            
        context['movimientos'] = InventarioService.obtener_historial_movimientos()
        context['form'] = ProductoForm()
        return context

class CrearProductoView(LoginRequiredMixin, AdminOrOperadorMixin, CreateView):
    """Alta de nuevos productos en el catálogo."""
    model = Producto
    form_class = ProductoForm
    template_name = 'dashboard.html'
    success_url = reverse_lazy('dashboard')

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
        return redirect('dashboard')

class EditarProductoView(LoginRequiredMixin, AdminOrOperadorMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'editar_producto.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        messages.success(self.request, "Producto modificado con éxito.")
        return super().form_valid(form)

    def get_context_data(**kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['rol'] = 'Admin'
        else:
            grupo = self.request.user.groups.first()
            context['rol'] = grupo.name if grupo else 'Consulta'
        return context

class EliminarProductoView(LoginRequiredMixin, AdminOrOperadorMixin, DeleteView):
    model = Producto
    template_name = 'dashboard.html'
    success_url = reverse_lazy('dashboard')
    pk_url_kwarg = 'producto_id'

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(request, "Producto eliminado correctamente.")
        return redirect(success_url)

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
        return redirect('dashboard')

class ExportarProductosCSVView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return InventarioService.generar_csv_productos()

class ExportarMovimientosCSVView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
            messages.error(request, "No tiene permisos.")
            return redirect('dashboard')
        return InventarioService.generar_csv_movimientos()

# --- VISTAS PARA LA SIMULACIÓN DE OPERACIONES (CORREGIDAS SIN INDEX OUT OF RANGE) ---

class SimularCompraView(LoginRequiredMixin, AdminOrOperadorMixin, View):
    """Permite seleccionar múltiples productos para simular un ingreso."""
    def get(self, request):
        productos = Producto.objects.all().order_by('nombre')
        return render(request, 'simular_compra.html', {'productos': productos})

    def post(self, request):
        productos_ids = request.POST.getlist('productos[]')
        
        if not productos_ids:
            messages.error(request, "Debe seleccionar al menos un producto.")
            return redirect('simular_compra')

        try:
            proveedor_defecto = Proveedor.objects.first()
            if not proveedor_defecto:
                proveedor_defecto = Proveedor.objects.create(nombre="Proveedor Sistema")

            compra = Compra.objects.create(usuario=request.user, proveedor=proveedor_defecto)
            resumen = []
            
            for p_id in productos_ids:
                # Obtenemos la cantidad específica de este ID de producto
                cant = request.POST.get(f'cantidad_{p_id}')
                cantidad = int(cant) if cant else 0
                
                if cantidad > 0:
                    mov = InventarioService.registrar_movimiento_stock(
                        producto_id=p_id, tipo='ENTRADA', cantidad=cantidad, usuario=request.user, compra_id=compra.id
                    )
                    resumen.append({'producto': mov.producto.nombre, 'cantidad': cantidad, 'precio': mov.producto.precio})
            
            return render(request, 'resumen_operacion.html', {'tipo': 'Compra', 'items': resumen, 'doc_id': compra.id})
        except Exception as e:
            messages.error(request, f"Error en la simulación: {str(e)}")
            return redirect('dashboard')


class SimularVentaView(LoginRequiredMixin, AdminOrOperadorMixin, View):
    """Permite seleccionar múltiples productos para simular un egreso con validación de stock."""
    def get(self, request):
        productos = Producto.objects.all().order_by('nombre')
        return render(request, 'simular_venta.html', {'productos': productos})

    def post(self, request):
        productos_ids = request.POST.getlist('productos[]')

        if not productos_ids:
            messages.error(request, "Debe seleccionar al menos un producto.")
            return redirect('simular_venta')

        try:
            cliente_defecto = Cliente.objects.first()
            if not cliente_defecto:
                cliente_defecto = Cliente.objects.create(nombre="Consumidor Final")

            venta = Venta.objects.create(usuario=request.user, cliente=cliente_defecto)
            resumen = []
            
            for p_id in productos_ids:
                # Obtenemos la cantidad específica de este ID de producto
                cant = request.POST.get(f'cantidad_{p_id}')
                cantidad = int(cant) if cant else 0
                
                if cantidad > 0:
                    mov = InventarioService.registrar_movimiento_stock(
                        producto_id=p_id, tipo='SALIDA', cantidad=cantidad, usuario=request.user, venta_id=venta.id
                    )
                    resumen.append({'producto': mov.producto.nombre, 'cantidad': cantidad, 'precio': mov.producto.precio})
            
            return render(request, 'resumen_operacion.html', {'tipo': 'Venta', 'items': resumen, 'doc_id': venta.id})
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('simular_venta')