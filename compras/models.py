from django.db import models
from django.contrib.auth.models import User

    
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    cuit = models.CharField(max_length=20, unique=True, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    
class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor.nombre}"
    
class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('inventario.Producto', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) 

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Compra #{self.compra.id})"