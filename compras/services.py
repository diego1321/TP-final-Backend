from compras.models import Compra, DetalleCompra
from inventario.models import Producto
from inventario.services import InventarioService
from decimal import Decimal
from django.db import transaction


class ComprasService:
    @staticmethod
    def obtener_historial_compras():
            return Compra.objects.all().select_related('proveedor', 'usuario').order_by('-fecha')
    @transaction.atomic
    @staticmethod
    def crear_compra(proveedor_id, usuario, items):
        """Crea la compra y registra sus detalles y movimientos."""
        compra = Compra.objects.create(proveedor_id=proveedor_id, usuario=usuario, total=0)
        total_compra = Decimal('0.00')
        
        for item in items: 
            producto = Producto.objects.get(id=item['id'])
            subtotal = Decimal(str(item['precio'])) * Decimal(str(item['cant']))
            
            DetalleCompra.objects.create(compra=compra, producto=producto, 
                                       cantidad=item['cant'], precio_unitario=item['precio'])
            
            InventarioService.registrar_movimiento_stock(producto.id, 'ENTRADA', item['cant'], usuario, compra_id=compra.id)
            
            total_compra += subtotal
            
        compra.total = total_compra
        compra.save()
        return compra