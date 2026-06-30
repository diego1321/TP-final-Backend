from decimal import Decimal

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .models import Producto, Movimiento, Compra, Venta, Proveedor, Cliente
from .forms import ClienteForm, ProductoForm, ProveedorForm
from .services import InventarioService
from django.views.generic import DetailView

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
class CrearProveedorView(LoginRequiredMixin, AdminOrOperadorMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'form_contacto.html' # Puedes usar un template genérico
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        messages.success(self.request, "Proveedor registrado con éxito.")
        return super().form_valid(form)

class CrearClienteView(LoginRequiredMixin, AdminOrOperadorMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'form_contacto.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        messages.success(self.request, "Cliente registrado con éxito.")
        return super().form_valid(form)

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
    def post(self, request, producto_id):
        producto = get_object_or_404(Producto, id=producto_id)
        producto.activo = False
        producto.save()
        messages.success(request, f"Producto {producto.nombre} desactivado correctamente.")
        return redirect('dashboard')

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
class VentaDetalleView(LoginRequiredMixin, AdminOrOperadorMixin, DetailView):
    model = Venta
    template_name = 'detalle_venta.html'
    context_object_name = 'venta'
    pk_url_kwarg = 'venta_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.detalles.all()
        return context

class CompraDetalleView(LoginRequiredMixin, AdminOrOperadorMixin, DetailView):
    model = Compra
    template_name = 'detalle_compra.html'
    context_object_name = 'compra'
    pk_url_kwarg = 'compra_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.detalles.all()
        return context
# --- VISTAS PARA LA SIMULACIÓN DE OPERACIONES (CORREGIDAS SIN INDEX OUT OF RANGE) ---

class SimularCompraView(LoginRequiredMixin, AdminOrOperadorMixin, View):
    """Permite seleccionar múltiples productos para simular un ingreso."""
    def get(self, request):
        productos = Producto.objects.filter(activo=True).order_by('nombre')
        proveedores = Proveedor.objects.all()
        return render(request, 'simular_compra.html', {'productos': productos, 'proveedores': proveedores})

    def post(self, request):
            productos_ids = request.POST.getlist('productos[]')
            proveedor_id = request.POST.get('proveedor_id')
            
            if not productos_ids:
                messages.error(request, "Debe seleccionar al menos un producto.")
                return redirect('simular_compra')
            if not proveedor_id: 
                messages.error(request, "Debe seleccionar un proveedor.")
                return redirect('simular_compra')
            try:
                items = []
                for p_id in productos_ids:
                    cant = request.POST.get(f'cantidad_{p_id}')
                    cantidad = int(cant) if cant else 0
                    costo_input = request.POST.get(f'costo_{p_id}')
                    precio_costo = Decimal(request.POST.get(f'costo_{p_id}', '0'))
                    
                    if cantidad > 0:
                        items.append({
                            'id': p_id, 
                            'cant': cantidad, 
                            'precio': precio_costo
                        })

                if not items:
                    messages.error(request, "Debe ingresar cantidades válidas.")
                    return redirect('simular_compra')
                compra = InventarioService.crear_compra(proveedor_id, request.user, items)
                
                resumen = [{'producto': item.producto.nombre, 'cantidad': item.cantidad, 'precio': item.precio_unitario} 
                        for item in compra.detalles.all()]
                
                return render(request, 'resumen_operacion.html', {'tipo': 'Compra', 'items': resumen, 'doc_id': compra.id})
                
            except Exception as e:
                messages.error(request, f"Error en la simulación: {str(e)}")
                return redirect('dashboard')


class SimularVentaView(LoginRequiredMixin, AdminOrOperadorMixin, View):
    """Permite seleccionar múltiples productos para simular un egreso con validación de stock."""
    def get(self, request):
        productos = Producto.objects.filter(activo=True).order_by('nombre')
        clientes = Cliente.objects.all()
        return render(request, 'simular_venta.html', {'productos': productos, 'clientes': clientes})

    def post(self, request):
            productos_ids = request.POST.getlist('productos[]')
            cliente_id = request.POST.get('cliente_id')
            if not productos_ids:
                messages.error(request, "Debe seleccionar al menos un producto.")
                return redirect('simular_venta')

            try:
                c_id = int(cliente_id) if cliente_id else None

                # 2. Preparamos la lista de items
                items = []
                for p_id in productos_ids:
                    cant = request.POST.get(f'cantidad_{p_id}')
                    cantidad = int(cant) if cant else 0
                    
                    if cantidad > 0:
                        items.append({
                            'id': p_id, 
                            'cant': cantidad
                        })

                if not items:
                    messages.error(request, "Debe ingresar cantidades válidas.")
                    return redirect('simular_venta')

                # 3. Llamamos al nuevo servicio (asumiendo que creaste crear_venta en services.py)
                venta = InventarioService.crear_venta(c_id, request.user, items)              
                # 4. Resumen para la vista
                resumen = [{'producto': item.producto.nombre, 'cantidad': item.cantidad, 'precio': item.precio_unitario} 
                    for item in venta.detalles.all()]
                
                return render(request, 'resumen_operacion.html', {'tipo': 'Venta', 'items': resumen, 'doc_id': venta.id})
                
            except Exception as e:
                messages.error(request, f"Error en la simulación: {str(e)}")
                return redirect('dashboard')

class HistoricoVentasView(LoginRequiredMixin, AdminOrOperadorMixin, ListView):
    model = Venta
    template_name = 'historico_ventas.html'
    context_object_name = 'ventas'

    def get_queryset(self):
        return InventarioService.obtener_historial_ventas()
    
class HistoricoComprasView(LoginRequiredMixin, AdminOrOperadorMixin, ListView):
    model = Compra
    template_name = 'historico_compras.html'
    context_object_name = 'compras'

    def get_queryset(self):
        return InventarioService.obtener_historial_compras()

class ExportarTicketPDFView(LoginRequiredMixin, View):
    def get(self, request, tipo, id):
        pdf = InventarioService.generar_pdf_ticket(tipo, id)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_{tipo}_{id}.pdf"'
        return response
class ProductosMasVendidosView(LoginRequiredMixin, AdminOrOperadorMixin, ListView):
    model = Producto
    template_name = 'productos_mas_vendidos.html'
    context_object_name = 'productos_top'

    def get_queryset(self):
        return InventarioService.obtener_productos_mas_vendidos(limite=10)