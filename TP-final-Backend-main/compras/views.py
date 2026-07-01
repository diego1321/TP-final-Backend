from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.views import View
from .forms import ProveedorForm
from inventario.models import Producto
from inventario.views import AdminOrOperadorMixin
from .services import ComprasService
from .models import Proveedor,Compra,DetalleCompra
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView, View, TemplateView

class SimularCompraView(LoginRequiredMixin, AdminOrOperadorMixin, View):
    """Permite seleccionar múltiples productos para simular un ingreso."""
    def get(self, request):
        productos = Producto.objects.filter(activo=True).order_by('nombre')
        proveedores = Proveedor.objects.all()
        return render(request, 'compras/simular_compra.html', {'productos': productos, 'proveedores': proveedores})

    def post(self, request):
            productos_ids = request.POST.getlist('productos[]')
            proveedor_id = request.POST.get('proveedor_id')
            
            if not productos_ids:
                messages.error(request, "Debe seleccionar al menos un producto.")
                return redirect('compras:simular_compra')
            if not proveedor_id: 
                messages.error(request, "Debe seleccionar un proveedor.")
                return redirect('compras:simular_compra')
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
                    return redirect('compras:simular_compra')
                compra = ComprasService.crear_compra(proveedor_id, request.user, items)
                
                resumen = [{'producto': item.producto.nombre, 'cantidad': item.cantidad, 'precio': item.precio_unitario} 
                        for item in compra.detalles.all()]
                
                return render(request, 'compras/resumen_operacion.html', {'tipo': 'Compra', 'items': resumen, 'doc_id': compra.id})
                
            except Exception as e:
                messages.error(request, f"Error en la simulación: {str(e)}")
                return redirect('inventario:dashboard')
            
class HistoricoComprasView(LoginRequiredMixin, AdminOrOperadorMixin, ListView):
    model = Compra
    template_name = 'compras/historico_compras.html'
    context_object_name = 'compras'

    def get_queryset(self):
        return ComprasService.obtener_historial_compras()

class CompraDetalleView(LoginRequiredMixin, AdminOrOperadorMixin, DetailView):
    model = Compra
    template_name = 'detalle_compra.html'
    context_object_name = 'compra'
    pk_url_kwarg = 'compra_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.detalles.all()
        return context
class CrearProveedorView(LoginRequiredMixin, AdminOrOperadorMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'form_contacto.html' # Puedes usar un template genérico
    success_url = reverse_lazy('inventario:dashboard')

    def form_valid(self, form):
        messages.success(self.request, "Proveedor registrado con éxito.")
        return super().form_valid(form)