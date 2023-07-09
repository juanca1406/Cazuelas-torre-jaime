from django.contrib import admin
from .models import Producto, Cliente, Pedido, Categoria
# Register your models here.


class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'producto', 'precio', 'categoria', 'stock', 'imagen')


class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'direccion', 'celular', 'fecha', 'estado')


class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'carrito', 'producto', 'cantidad')


class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria')


admin.site.register(Pedido, PedidoAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente, ClienteAdmin)
admin.site.register(Categoria, CategoriaAdmin)
