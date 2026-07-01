from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from inventario.models import Producto
from inventario.services import InventarioService
from inventario.views import AdminOrOperadorMixin
from ventas.forms import ClienteForm
from ventas.models import Cliente, Venta,DetalleVenta
from .services import VentasService
from django.views.generic import DetailView,ListView, CreateView, UpdateView, DeleteView, View, TemplateView


class SimularVentaView(LoginRequiredMixin, AdminOrOperadorMixin, View):
    """Permite seleccionar múltiples productos para simular un egreso con validación de stock."""
    def get(self, request):
        productos = Producto.objects.filter(activo=True).order_by('nombre')
        clientes = Cliente.objects.all()
        return render(request, 'ventas/simular_venta.html', {'productos': productos, 'clientes': clientes})

    def post(self, request):
            productos_ids = request.POST.getlist('productos[]')
            cliente_id = request.POST.get('cliente_id')
            if not productos_ids:
                messages.error(request, "Debe seleccionar al menos un producto.")
                return redirect('ventas:simular_venta')

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
                    return redirect('ventas:simular_venta')

                # 3. Llamamos al nuevo servicio (asumiendo que creaste crear_venta en services.py)
                venta = VentasService.crear_venta(c_id, request.user, items)              
                # 4. Resumen para la vista
                resumen = [{'producto': item.producto.nombre, 'cantidad': item.cantidad, 'precio': item.precio_unitario} 
                    for item in venta.detalles.all()]
                
                return render(request, 'ventas/resumen_operacion.html', {'tipo': 'Venta', 'items': resumen, 'doc_id': venta.id})
                
            except Exception as e:
                messages.error(request, f"Error en la simulación: {str(e)}")
                return redirect('inventario:dashboard')
            
class HistoricoVentasView(LoginRequiredMixin, AdminOrOperadorMixin, ListView):
    model = Venta
    template_name = 'ventas/historico_ventas.html'
    context_object_name = 'ventas'

    def get_queryset(self):
        return VentasService.obtener_historial_ventas()
    
class VentaDetalleView(LoginRequiredMixin, AdminOrOperadorMixin, DetailView):
    model = Venta
    template_name = 'ventas/detalle_venta.html'
    context_object_name = 'venta'
    pk_url_kwarg = 'venta_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.detalles.all()
        return context
class CrearClienteView(LoginRequiredMixin, AdminOrOperadorMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'form_contacto.html'
    success_url = reverse_lazy('inventario:dashboard')

    def form_valid(self, form):
        messages.success(self.request, "Cliente registrado con éxito.")
        return super().form_valid(form)
class ExportarTicketPDFView(LoginRequiredMixin, View):
    def get(self, request, tipo, id):
        pdf = VentasService.generar_pdf_ticket(tipo, id)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="ticket_{tipo}_{id}.pdf"'
        return response