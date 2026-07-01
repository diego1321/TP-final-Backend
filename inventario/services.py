import csv
from io import BytesIO
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .models import Producto, Movimiento
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from decimal import Decimal
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

class InventarioService:
    @staticmethod
    def obtener_todos_los_productos():
        return Producto.objects.all().select_related('categoria').order_by('id')

    @staticmethod
    def obtener_historial_movimientos():
        return Movimiento.objects.all().select_related('producto', 'usuario', 'compra', 'venta').order_by('-fecha')

    @staticmethod   
    @transaction.atomic
    def registrar_movimiento_stock(producto_id, tipo, cantidad, usuario, compra_id=None, venta_id=None):
            try:
            # 🌟 CAMBIO AQUÍ: Agregamos activo=True al .get()
                producto = Producto.objects.select_for_update().get(id=producto_id, activo=True)
            except (ObjectDoesNotExist, ValueError, TypeError):
                raise ValidationError("El producto seleccionado no está activo, no es válido o ya no existe.")
            """Solo registra el movimiento físico y la relación con el documento."""
            producto = Producto.objects.select_for_update().get(id=producto_id)
            
            if tipo == 'SALIDA' and producto.cantidad < cantidad:
                raise ValidationError(f"Stock insuficiente para {producto.nombre}.")
                
            if tipo == 'ENTRADA':
                producto.cantidad += cantidad
            else:
                producto.cantidad -= cantidad
            producto.save()

            return Movimiento.objects.create(
                producto=producto,
                tipo=tipo,
                cantidad=cantidad,
                usuario=usuario,
                compra_id=compra_id,
                venta_id=venta_id
            )

    @staticmethod
    def generar_csv_productos():
        # Usamos la codificación 'latin-1' que es nativa y perfectamente compatible con Excel en Windows
        response = HttpResponse(content_type='text/csv; charset=latin-1')
        response['Content-Disposition'] = 'attachment; filename="productos.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Producto', 'Categoria', 'Stock Disponible', 'Precio Unitario'])
        
        for p in Producto.objects.all().select_related('categoria').order_by('id'):
            nombre_categoria = p.categoria.nombre if p.categoria else "Sin categoria"
            # Eliminamos tildes conflictivas de forma manual si es necesario para evitar fallos de codificación
            cat_limpia = nombre_categoria.replace('í', 'i',).replace('ó', 'o')
            writer.writerow([p.id, p.nombre, cat_limpia, p.cantidad, p.precio])
            
        return response

    @staticmethod
    def generar_csv_movimientos():
        response = HttpResponse(content_type='text/csv; charset=latin-1')
        response['Content-Disposition'] = 'attachment; filename="movimientos.csv"'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Producto', 'Tipo', 'Cantidad', 'Usuario', 'Fecha', 'Doc. Referencia'])
        
        movimientos = Movimiento.objects.all().select_related('producto', 'usuario', 'compra', 'venta').order_by('id')
        
        for m in movimientos:
            fecha_local = timezone.localtime(m.fecha)
            referencia = "N/A"
            if m.compra:
                referencia = f"Compra #{m.compra.id}"
            elif m.venta:
                referencia = f"Venta #{m.venta.id}"
                
            writer.writerow([
                m.id,
                m.producto.nombre,
                m.tipo,
                m.cantidad,
                m.usuario.username,
                fecha_local.strftime('%Y-%m-%d %H:%M:%S'),
                referencia
            ])
            
        return response

    @staticmethod
    def obtener_productos_mas_vendidos(limite=5):
        return Producto.objects.annotate(
            total_vendido=Sum('detalleventa__cantidad') 
        ).filter(
            total_vendido__gt=0
        ).order_by('-total_vendido')[:limite]