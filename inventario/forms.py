from django import forms
from .models import Cliente, Producto, Categoria,Proveedor

class ProductoForm(forms.ModelForm):
    cantidad_inicial = forms.IntegerField(
        label="Stock Inicial", 
        required=False, 
        initial=0,
        min_value=0
    )

    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'categoria']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance.pk:
            self.fields.pop('cantidad_inicial', None)
        
        self.fields['categoria'].required = True
        self.fields['categoria'].empty_label = "Seleccione una categoría"
        
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'cuit', 'telefono', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'dni_cuit', 'email']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})