from django import forms
from django.forms import ModelForm
from .models import Producto, Categoria


class ProductoForm(ModelForm):
    class Meta:
        model = Producto
        fields = ('producto', 'precio', 'imagen', 'categoria', 'stock')
        widgets = {
            'precio': forms.NumberInput(attrs={'step': 'any'}),
        }


class CategoriaForm(ModelForm):
    class Meta:
        model = Categoria
        fields = ("categoria",)
