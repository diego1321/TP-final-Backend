from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

# gestion_stock/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('admin/', admin.site.urls),
    path('inventario/', include('inventario.urls')),
    path('compras/', include('compras.urls')),
    path('ventas/', include('ventas.urls')),
    path('', RedirectView.as_view(url='inventario/', permanent=True)),
    path('accounts/', include('django.contrib.auth.urls')),

    ]
