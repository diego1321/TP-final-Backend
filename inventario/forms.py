from django import forms
from .models import Producto, Categoria

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
        self.fields['categoria'].required = True
        self.fields['categoria'].empty_label = "Seleccione una categoría"
        
        for field in self.fields.values():    
            field.widget.attrs['class'] = 'form-control'
