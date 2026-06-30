import csv
from io import BytesIO
from django.http import HttpResponse
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Sum
from .models import Producto, Movimiento, Compra, Venta, DetalleCompra, DetalleVenta,Proveedor,Cliente
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from decimal import Decimal

class InventarioService:
    @staticmethod
    def obtener_todos_los_productos():
        return Producto.objects.filter(activo=True).select_related('categoria').order_by('id')

    @staticmethod
    def obtener_historial_movimientos():
        return Movimiento.objects.all().select_related('producto', 'usuario', 'compra', 'venta').order_by('-fecha')
    
    @staticmethod
    def obtener_productos_mas_vendidos(limite=5):
        """Calcula el Top de productos con mayor cantidad vendida históricamente."""
        return Producto.objects.annotate(
            total_vendido=Sum('detalleventa__cantidad')
        ).filter(
            total_vendido__gt=0
        ).order_by('-total_vendido')[:limite]
    
    @staticmethod
    def obtener_historial_ventas():
        return Venta.objects.all().select_related('cliente', 'usuario').order_by('-fecha')

    @staticmethod
    def obtener_historial_compras():
        return Compra.objects.all().select_related('proveedor', 'usuario').order_by('-fecha')

    @staticmethod
    def generar_pdf_ticket(tipo, objeto_id):
        """Genera un PDF usando WeasyPrint basado en un template HTML."""
        if tipo == 'venta':
            data = Venta.objects.get(id=objeto_id)
            template = 'pdf/ticket_venta.html'
        else:
            data = Compra.objects.get(id=objeto_id)
            template = 'pdf/ticket_compra.html'
            
        html_string = render_to_string(template, {'objeto': data, 'items': data.detalles.all()})
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        
        if not pdf.err:
            return result.getvalue()
        return None
    @staticmethod   
    @transaction.atomic
    def registrar_movimiento_stock(producto_id, tipo, cantidad, usuario, compra_id=None, venta_id=None):
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
    @transaction.atomic
    def crear_compra(proveedor_id, usuario, items):
        """Crea la compra y registra sus detalles y movimientos."""
        compra = Compra.objects.create(proveedor_id=proveedor_id, usuario=usuario, total=0)
        total_compra = Decimal('0.00')
        
        for item in items: # items debería ser una lista de dicts {'id', 'cant', 'precio'}
            producto = Producto.objects.get(id=item['id'])
            subtotal = Decimal(str(item['precio'])) * Decimal(str(item['cant']))
            
            DetalleCompra.objects.create(compra=compra, producto=producto, 
                                       cantidad=item['cant'], precio_unitario=item['precio'])
            
            InventarioService.registrar_movimiento_stock(producto.id, 'ENTRADA', item['cant'], usuario, compra_id=compra.id)
            
            total_compra += subtotal
            
        compra.total = total_compra
        compra.save()
        return compra
    @staticmethod
    @transaction.atomic
    def crear_venta(cliente_id, usuario, items):
        """Crea la venta y registra sus detalles y movimientos."""
        venta = Venta.objects.create(cliente_id=cliente_id, usuario=usuario, total=0)
        total_venta = Decimal('0.00')
        
        for item in items:
            producto = Producto.objects.get(id=item['id'])
            subtotal = producto.precio * Decimal(str(item['cant']))
            
            DetalleVenta.objects.create(venta=venta, producto=producto, 
                                      cantidad=item['cant'], precio_unitario=producto.precio)
            
            InventarioService.registrar_movimiento_stock(producto.id, 'SALIDA', item['cant'], usuario, venta_id=venta.id)
            
            total_venta += subtotal
            
        venta.total = total_venta
        venta.save()
        return venta
    @staticmethod
    def generar_csv_productos():
        # Usamos la codificación 'latin-1' que es nativa y perfectamente compatible con Excel en Windows
        response = HttpResponse(content_type='text/csv; charset=latin-1')
        response['Content-Disposition'] = 'attachment; filename="productos.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Producto', 'Categoria', 'Stock Disponible', 'Precio Unitario'])
        
        for p in Producto.objects.all().select_related('categoria').order_by('id'):
            nombre_categoria = p.categoria.nombre if p.categoria else "Sin categoria"
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