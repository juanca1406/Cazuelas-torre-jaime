from django.urls import path
from . import views

app_name = 'productos'
urlpatterns = [
    path('', views.index, name="index"),
    path('detalle/', views.detalle, name="detalle"),
    path('agregar/<int:producto_id>', views.agregar, name="agregar"),
    path('eliminar/<int:producto_id>', views.eliminar, name="eliminar"),
    path('modificar_cantidad/<int:producto_id>/<int:nueva_cantidad>',
         views.modificar_cantidad, name="modificar_cantidad"),
    path('registrar/',
         views.registrar, name="registrar"),
    path('registro_pedido/',
         views.registro_pedido, name="registro_pedido"),
    path('bebidas/', views.bebidas, name="bebidas"),
    path('adicciones/', views.adicciones, name="adicciones"),
    path('todos/', views.todos, name="todos"),
    path('salir/', views.salir, name="salir"),
    path('cliente/', views.cliente, name="cliente"),
    path('administrador/', views.administrador, name="administrador"),
    path('pedidos/', views.pedidos, name="pedidos"),
    path('pedidos_realizados/', views.pedidos_realizados,
         name="pedidos_realizados"),
    path('estado/<int:producto_id>', views.estado, name="estado"),
    path('productos/', views.productos, name="productos"),
    path('stock/<int:producto_id>', views.stock, name="stock"),
    path('agregarp/', views.agregarp, name="agregarp"),
    path('categoria/', views.categoria, name="categoria"),
    path('categoriap/', views.categoriap, name="categoriap"),
    path('categoriae/<int:producto_id>', views.categoriae, name="categoriae"),
    path('categoria_eliminar/<int:producto_id>',
         views.categoria_eliminar, name="categoria_eliminar"),
    path('detalles/<int:producto_id>', views.detalles, name="detalles"),
    path('modificar/<int:producto_id>', views.modificar, name="modificar"),
    path('informes/', views.informes, name="informes"),
    path('registro_hoy/', views.registro_hoy, name="registro_hoy"),
    path('ajustes/', views.ajustes, name="ajustes"),
    path('pdf/<int:producto_id>', views.pdf, name="pdf"),
    path('pdf_carrito/', views.pdf_carrito, name="pdf_carrito"),
    path('contactos/', views.contactos, name="contactos"),
    path('tomar_pedidos/', views.tomar_pedidos, name="tomar_pedidos"),
    path('mostrar/', views.mostrar, name="mostrar"),
    path('agregar_productos/', views.agregar_productos, name="agregar_productos"),
    path('agregars/<int:producto_id>', views.agregars, name="agregars"),
    path('modificars/<int:producto_id>/<int:nueva_cantidad>',
         views.modificars, name="modificars"),
    path('eliminars/<int:producto_id>', views.eliminars, name="eliminars"),

]
