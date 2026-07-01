from django.urls import path
from django.contrib import admin
from django.contrib.auth import views as auth_views
from .views import CrearProductoView, DashboardView, EditarProductoView, EliminarProductoView, ExportarMovimientosCSVView, ExportarProductosCSVView, ProductosMasVendidosView, RegistrarMovimientoView
app_name = 'inventario'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('productos/top/', ProductosMasVendidosView.as_view(), name='productos_top'),
    path('productos/crear/', CrearProductoView.as_view(), name='crear_producto'),
    path('productos/<int:pk>/editar/', EditarProductoView.as_view(), name='editar_producto'),
    path('productos/<int:pk>/eliminar/', EliminarProductoView.as_view(), name='eliminar_producto'),
    path('movimientos/registrar/', RegistrarMovimientoView.as_view(), name='registrar_movimiento'),
    path('exportar/movimientos/', ExportarMovimientosCSVView.as_view(), name='exportar_movimientos'),
    path('exportar/productos/', ExportarProductosCSVView.as_view(), name='exportar_productos'),
    ]