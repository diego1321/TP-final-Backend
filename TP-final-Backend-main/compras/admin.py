from django.contrib import admin

from compras.models import Compra,Proveedor,DetalleCompra

admin.site.register(Compra)
admin.site.register(Proveedor)
admin.site.register(DetalleCompra)
