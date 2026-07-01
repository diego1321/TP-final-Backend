from django.contrib import admin

from ventas.models import Venta, Cliente, DetalleVenta

admin.site.register(Venta)
admin.site.register(Cliente)
admin.site.register(DetalleVenta)
