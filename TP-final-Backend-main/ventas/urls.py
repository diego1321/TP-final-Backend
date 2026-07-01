from django.urls import path
from inventario.views import ExportarMovimientosCSVView
from .views import CrearClienteView, SimularVentaView, HistoricoVentasView, VentaDetalleView, ExportarTicketPDFView

app_name = 'ventas'
urlpatterns = [
    path('simular/venta/', SimularVentaView.as_view(), name='simular_venta'),
    path('historico/ventas/', HistoricoVentasView.as_view(), name='historico_ventas'),
    path('historial/ventas/', HistoricoVentasView.as_view(), name='historico_ventas'),
    path('cliente/nuevo/', CrearClienteView.as_view(), name='crear_cliente'),
    path('ticket/pdf/<str:tipo>/<int:id>/', ExportarTicketPDFView.as_view(), name='generar_pdf'),
    
    
    ]