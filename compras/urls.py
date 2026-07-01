# compras/urls.py
from django.urls import path
from .views import CrearProveedorView, SimularCompraView, HistoricoComprasView, CompraDetalleView
app_name = 'compras'
urlpatterns = [
    path('simular/', SimularCompraView.as_view(), name='simular_compra'),
    path('historico/', HistoricoComprasView.as_view(), name='historico_compras'),
    path('detalle/<int:compra_id>/', CompraDetalleView.as_view(), name='detalle_compra'),
    path('proveedor/nuevo/', CrearProveedorView.as_view(), name='crear_proveedor'),
]