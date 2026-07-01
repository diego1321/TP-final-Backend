from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='productos', null=True, blank=True)
    cantidad = models.IntegerField(default=0)  # Representa el Stock
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

    
class Movimiento(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada (Ingreso por Compra)'),
        ('SALIDA', 'Salida (Egreso por Venta)'),
    ]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    compra = models.ForeignKey('compras.Compra', on_delete=models.SET_NULL, null=True, blank=True)
    venta = models.ForeignKey('ventas.Venta', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"