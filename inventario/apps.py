from django.apps import AppConfig
from django.db.models.signals import post_migrate

def cargar_categorias_automaticas(sender, **kwargs):
    
    try:
        from .models import Categoria
        
        lista_cat = [
            "Tecnología y Electrónica", 
            "Electrodomésticos", 
            "Hogar y Muebles",
            "Bazar y Cocina", 
            "Herramientas y Ferretería", 
            "Deportes y Fitness",
            "Moda y Calzado", 
            "Salud y Belleza", 
            "Alimentos y Bebidas", 
            "Librería y Oficina"
        ]

        for nombre in lista_cat:
            Categoria.objects.get_or_create(nombre=nombre)
            
    except Exception:
        pass

class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'

    def ready(self):
        post_migrate.connect(cargar_categorias_automaticas, sender=self)