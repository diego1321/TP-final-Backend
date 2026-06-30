from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from inventario import views

urlpatterns = [
    
    path('admin/', admin.site.urls),
    
    
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
   
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('crear-producto/', views.CrearProductoView.as_view(), name='crear_producto'),
    path('editar-producto/<int:pk>/', views.EditarProductoView.as_view(), name='editar_producto'),
    path('eliminar-producto/<int:producto_id>/', views.EliminarProductoView.as_view(), name='eliminar_producto'),
    path('movimiento/', views.RegistrarMovimientoView.as_view(), name='registrar_movimiento'),
    
    
    path('exportar/', views.ExportarProductosCSVView.as_view(), name='exportar_csv'),
    path('exportar-movimientos/', views.ExportarMovimientosCSVView.as_view(), name='exportar_csv_movimientos'),
]