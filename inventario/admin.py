from django.contrib import admin
from .models import Cliente, Proveedor, Categoria, Producto, Compra, Venta, Movimiento

admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(Compra)
admin.site.register(Venta)
admin.site.register(Movimiento)