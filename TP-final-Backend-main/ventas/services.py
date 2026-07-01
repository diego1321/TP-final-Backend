from django.db.models import Sum
from compras.models import Compra
from inventario.models import Producto
from ventas.models import Venta
from xhtml2pdf import pisa
from io import BytesIO
from django.db.models import Sum
from django.template.loader import render_to_string
from django.db import transaction
from decimal import Decimal
from .models import DetalleVenta,Venta,Cliente
from inventario.services import InventarioService

class VentasService:
    
    def obtener_historial_ventas():
        return Venta.objects.all().select_related('cliente', 'usuario').order_by('-fecha')
    
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