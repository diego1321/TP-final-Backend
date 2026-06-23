from django.db import models
from django.contrib.auth.models import User 
from django.core.exceptions import ValidationError

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad = models.IntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class Movimiento(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada (Ingreso)'),
        ('SALIDA', 'Salida (Egreso)'),
    ]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)
    def save(self, *args, **kwargs):
        if self.tipo == 'SALIDA' and self.producto.cantidad < self.cantidad:
            raise ValidationError(f"🚫 Stock insuficiente. Solo quedan {self.producto.cantidad} unidades.")

        # Modificar el stock del producto según el tipo de movimiento
        if self.tipo == 'ENTRADA':
            self.producto.cantidad += self.cantidad
        elif self.tipo == 'SALIDA':
            self.producto.cantidad -= self.cantidad
        
        self.producto.save()

        # 4. Guardar efectivamente el movimiento en la base de datos
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"