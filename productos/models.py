from django.db import models

# Create your models here.


class Categoria(models.Model):
    categoria = models.CharField(max_length=300)

    def __str__(self):
        return self.categoria


class Producto(models.Model):
    producto = models.CharField(max_length=250)
    precio = models.FloatField()
    imagen = models.ImageField(upload_to="productos", null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    stock = models.IntegerField()

    def __str__(self):
        return self.producto


class Cliente(models.Model):
    nombre = models.CharField(max_length=250)
    direccion = models.CharField(max_length=350)
    celular = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.IntegerField()

    def __str__(self):
        return f"Carrito #{self.id}"


class Pedido(models.Model):
    carrito = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def subtotal(self):
        return self.producto.precio * self.cantidad


class Ventas(models.Model):
    producto = models.CharField(max_length=300)
    precio = models.FloatField()
    imagen = models.ImageField(upload_to="ventas", null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    stock = models.IntegerField()
    limited = models.BooleanField(default=False)
