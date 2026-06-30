from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from inventario.views import (
    CrearClienteView, CrearProveedorView, DashboardView, CrearProductoView, EditarProductoView, EliminarProductoView, ExportarTicketPDFView, HistoricoVentasView, ProductosMasVendidosView,
    RegistrarMovimientoView, ExportarProductosCSVView, ExportarMovimientosCSVView,
    SimularCompraView, SimularVentaView,HistoricoComprasView,HistoricoVentasView
)

urlpatterns = [
    # Administración nativa de Django
    path('admin/', admin.site.urls),

    # Autenticación nativa del sistema
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Panel de control e Inventario
    path('', DashboardView.as_view(), name='dashboard'),
    
    # ABM de Productos
    path('producto/crear/', CrearProductoView.as_view(), name='crear_producto'),
    path('producto/editar/<int:pk>/', EditarProductoView.as_view(), name='editar_producto'),
    path('producto/eliminar/<int:producto_id>/', EliminarProductoView.as_view(), name='eliminar_producto'),
    
    # Movimientos individuales y descargas
    path('movimiento/registrar/', RegistrarMovimientoView.as_view(), name='registrar_movimiento'),
    path('exportar/productos/', ExportarProductosCSVView.as_view(), name='exportar_csv'),
    path('exportar/movimientos/', ExportarMovimientosCSVView.as_view(), name='exportar_csv_movimientos'),
    
    # Nuevas simulaciones masivas
    path('simular/compra/', SimularCompraView.as_view(), name='simular_compra'),
    path('simular/venta/', SimularVentaView.as_view(), name='simular_venta'),
    path('historico/ventas/', HistoricoVentasView.as_view(), name='historico_ventas'),
    path('ticket/pdf/<str:tipo>/<int:id>/', ExportarTicketPDFView.as_view(), name='generar_pdf'),
    path('historial/ventas/', HistoricoVentasView.as_view(), name='historico_ventas'),
    path('historial/compras/', HistoricoComprasView.as_view(), name='historico_compras'),
    
    path('ticket/pdf/<str:tipo>/<int:id>/', ExportarTicketPDFView.as_view(), name='generar_pdf'),
    path('cliente/nuevo/', CrearClienteView.as_view(), name='crear_cliente'),
    path('proveedor/nuevo/', CrearProveedorView.as_view(), name='crear_proveedor'),
    path('productos/top/', ProductosMasVendidosView.as_view(), name='productos_top'),

]