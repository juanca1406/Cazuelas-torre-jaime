import pytz
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Cliente, Pedido, Categoria
import locale
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import ProductoForm, CategoriaForm
from django.core.paginator import Paginator
from django.core.mail import send_mail
import datetime

# Create your views here.


def bebidas(request):
    categoria = Categoria.objects.get(categoria='Bebidas')
    productos = Producto.objects.filter(categoria=categoria)
    carrito = request.session.get('carrito', [])
    cantidadp = sum(producto['cantidad'] for producto in carrito)
    return render(
        request,
        'categoria/bebidas.html',
        context={'productos': productos, 'cantidadp': cantidadp}
    )


def index(request):
    categoria = Categoria.objects.get(categoria='Cazuela')
    productos = Producto.objects.filter(categoria=categoria)
    carrito = request.session.get('carrito', [])
    cantidadp = sum(producto['cantidad'] for producto in carrito)
    return render(
        request,
        'index.html',
        context={'productos': productos, 'cantidadp': cantidadp}
    )


def todos(request):
    productos = Producto.objects.all()
    carrito = request.session.get('carrito', [])
    cantidadp = sum(producto['cantidad'] for producto in carrito)
    return render(
        request,
        'categoria/todos.html',
        context={'productos': productos, 'cantidadp': cantidadp}
    )


def agregar(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', [])

    for item in carrito:
        if item['producto_id'] == producto_id:
            item['cantidad'] += 1
            break
    else:
        item = {'producto_id': producto_id, 'cantidad': 1}
        carrito.append(item)

    request.session['carrito'] = carrito
    # para saber la cantidad del total
    cantidad_total = sum(item['cantidad'] for item in carrito)

    return JsonResponse({'mensaje': 'Producto agregado al carrito correctamente.', 'cantidad_total': cantidad_total})


def detalle(request):
    carrito = request.session.get('carrito', [])
    cantidadp = len(carrito)
    carrito_ids = [item['producto_id']
                   for item in carrito if isinstance(item, dict)]
    carrito_productos = Producto.objects.filter(pk__in=carrito_ids)

    total = 0

    # Agregar la cantidad y subtotal a cada producto del carrito
    for producto in carrito_productos:
        item = next((item for item in carrito if isinstance(
            item, dict) and item['producto_id'] == producto.id), None)
        if item:
            producto.cantidad = item['cantidad']
            producto.subtotal = producto.precio * producto.cantidad
            total += producto.subtotal
            locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

            # Formatear el precio y el subtotal con puntos como separadores de miles
            producto.precio_formateado = locale.format_string(
                '%.0f', producto.precio, grouping=True)
            producto.subtotal_formateado = locale.format_string(
                '%.0f', producto.subtotal, grouping=True)
        else:
            producto.cantidad = 0
            producto.subtotal = 0

    total_formateado = locale.format_string('%.0f', total, grouping=True)

    return render(request, 'detalle.html', {'carrito': carrito_productos, 'total': total,
                                            'total_formateado': total_formateado, 'cantidadp': cantidadp})


def eliminar(request, producto_id):
    carrito = request.session.get('carrito', [])

    for item in carrito:
        if item['producto_id'] == producto_id:
            carrito.remove(item)
            break

    request.session['carrito'] = carrito
    return redirect('/detalle/')


def modificar_cantidad(request, producto_id, nueva_cantidad):
    carrito = request.session.get('carrito', [])

    for item in carrito:
        if item['producto_id'] == producto_id:
            item['cantidad'] = nueva_cantidad
            break

    request.session['carrito'] = carrito

    request.session.modified = True  # Indica que la sesión ha sido modificada
    print(carrito)
    return redirect('/detalle')


def adicciones(request):
    categoria = Categoria.objects.get(categoria='Adicciones')
    productos = Producto.objects.filter(categoria=categoria)
    carrito = request.session.get('carrito', [])
    cantidadp = sum(producto['cantidad'] for producto in carrito)
    return render(
        request,
        'categoria/adicciones.html',
        context={'productos': productos, 'cantidadp': cantidadp}
    )


def registrar(request):
    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        direccion = request.POST.get('direccion')
        celular = request.POST.get('celular')
        estado = request.POST.get('estado')

        cliente = Cliente(nombre=nombre, direccion=direccion,
                          celular=celular, estado=estado)
        cliente.save()

        # Guardar los productos del carrito en la base de datos
        carrito = request.session.get('carrito', [])

        for item in carrito:
            if isinstance(item, dict):
                producto_id = item['producto_id']
                cantidad = item['cantidad']
                producto = Producto.objects.get(id=producto_id)

                # Crear el item del carrito asociado al cliente y producto
                item_carrito = Pedido(
                    carrito=cliente, producto=producto, cantidad=cantidad)
                item_carrito.save()

        # Eliminar el carrito de la sesión después de guardar los datos en la base de datos
        del request.session['carrito']

        total = 0
        for producto in carrito:
            if isinstance(producto, dict):
                producto_id = producto['producto_id']
                cantidad = producto['cantidad']
                producto_obj = Producto.objects.get(id=producto_id)
                subtotal = producto_obj.precio * cantidad
                total += subtotal

        total_formateado = locale.format_string('%.0f', total, grouping=True)

       # crear el cuerpo
        cuerpo_correo = f'Cazuelas torre jaime,\n\nInformacion del usuario:\n\n'
        cuerpo_correo += f'Nombre: {nombre}\n'
        cuerpo_correo += f'Dirección: {direccion}\n'
        cuerpo_correo += f'Celular: {celular}\n\n'
        cuerpo_correo += 'Detalles del carrito:\n'

        for producto in carrito:
            if isinstance(producto, dict):
                producto_id = producto['producto_id']
                cantidad = producto['cantidad']
                producto_obj = Producto.objects.get(id=producto_id)
                subtotal = producto_obj.precio * cantidad

                cuerpo_correo += f'- Producto: {producto_obj.producto}, Cantidad: {cantidad}, Subtotal: {subtotal}\n'

        cuerpo_correo += f'Total: {total_formateado}\n'

        # Enviar correo electrónico
        send_mail(
            'Registro de usuario',
            cuerpo_correo,
            'yersonhenao45@gmail.com',
            ['tucorreo@example.com'],
            fail_silently=False,
        )

        return redirect('/registro_pedido/')

    carrito = request.session.get('carrito', [])
    carrito_ids = [item['producto_id']
                   for item in carrito if isinstance(item, dict)]
    carrito_productos = Producto.objects.filter(pk__in=carrito_ids)

    # Configurar la localización según tus preferencias
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

    for producto in carrito_productos:
        item = next((item for item in carrito if isinstance(
            item, dict) and item['producto_id'] == producto.id), None)
        if item:
            producto.cantidad = item['cantidad']
            producto.subtotal = producto.precio * producto.cantidad

            producto.subtotal_formateado = locale.format_string(
                '%.0f', producto.subtotal, grouping=True)
        else:
            producto.cantidad = 0
            producto.subtotal = 0
    total = sum(producto.subtotal for producto in carrito_productos)

    total_formateado = locale.format_string('%.0f', total, grouping=True)

    cantidadp = len(carrito)
    return render(
        request,
        'registrar.html',
        {
            'carrito': carrito_productos,
            'cantidadp': cantidadp,
            'total_formateado': total_formateado
        }
    )


def registro_pedido(request):
    pedidor = Pedido.objects.latest('carrito_id')
    pedidores = Pedido.objects.filter(carrito_id=pedidor.carrito_id)
    total = sum(pedidor.subtotal() for pedidor in pedidores)
    return render(
        request,
        'registro_pedido.html',
        context={'pedidor': pedidor, 'pedidores': pedidores, 'total': total}
    )


def pdf_carrito(request):
    cliente = Pedido.objects.latest('carrito_id')
    pedido = Pedido.objects.filter(carrito_id=cliente.carrito_id)

    context = {
        'nombre': cliente.carrito.nombre,
        'direccion': cliente.carrito.direccion,
        'fecha': cliente.carrito.fecha,
        'celular': cliente.carrito.celular,
        'productos': [],
        'total': 0,
    }

    for pedido in pedido:
        producto = {
            'nombre': pedido.producto.producto,
            'cantidad': pedido.cantidad,
            'precio': pedido.producto.precio,

        }
        producto['subtotal'] = producto['precio'] * \
            producto['cantidad']
        context['productos'].append(producto)
        context['total'] += producto['subtotal']

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="factura.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

    color = '#0093FF'
    p.saveState()
    p.setFillColor(HexColor(color))
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 680, 'CAZUELAS TORREJAIME')
    p.restoreState()
    p.setFont("Arial", 10)
    p.drawString(50, 660, 'Nit. 21.591.833-1')
    p.drawString(50, 640, 'Direccion: Cl. 7 #18-72, Girardota, Antioquia')
    p.drawString(50, 620, 'Celular: 302 8348422')
    p.drawString(50, 600, 'Email: cazuelastorrejuan@gmail.com')
    imagen = 'productos\static\icono\icono.jpeg'

    x = 100
    y = 700
    width = 100
    height = 100

    imagen = ImageReader(imagen)
    p.drawImage(imagen, x, y, width, height)

    colombia_tz = pytz.timezone('America/Bogota')
    current_time = datetime.datetime.now(colombia_tz)
    context['fecha'] = current_time.strftime('%Y-%m-%d %H:%M:%S')

    p.drawString(50, 570, 'Fecha del pedido: {}'.format(context['fecha']))
    p.drawString(50, 550, 'Nombre: {}'.format(context['nombre']))
    p.drawString(50, 510, 'Celular: {}'.format(context['celular']))
    p.drawString(50, 530, 'Dirección: {}'.format(context['direccion']))

    data = [['                            Producto                               ',
             '   Cantidad   ', '     Precio    ', '       Subtotal       ']]
    for producto in context['productos']:
        nombre = producto['nombre']
        cantidad = producto['cantidad']
        precio = producto['precio']
        subtotal = precio * cantidad
        data.append([nombre, str(cantidad), str(precio), str(subtotal)])

    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1753C9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-0, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    table = Table(data)
    table.setStyle(TableStyle(table_style))

    table.wrapOn(p, 100, 200)
    table.drawOn(p, 50, y - 245)

    p.drawString(
        130, 420, '*** Para poder realizar un reclamo o devolución debe de presentar esta factura ***')

    p.setFont("Helvetica-Bold", 12)
    total_formateado = locale.format_string(
        '%.0f', context['total'], grouping=True)

    p.drawString(475, y - 260, 'Total: {}'.format(total_formateado))

    p.showPage()
    p.save()

    return response


def contactos(request):
    carrito = request.session.get('carrito', [])
    cantidadp = sum(producto['cantidad'] for producto in carrito)
    return render(
        request,
        'contactos.html',
        context={'cantidadp': cantidadp}
    )


@login_required
def login(request):
    return render(
        request,
        'cliente.html'
    )


@login_required
def administrador(request):
    numeroto = Pedido.objects.filter(carrito__estado='2').values(
        'carrito').distinct().count()
    numerop = Pedido.objects.filter(carrito__estado='1').values(
        'carrito').distinct().count()
    numeropr = Producto.objects.all().count()
    return render(
        request,
        'panel/admin.html',
        context={'numerop': numerop,
                 'numeropr': numeropr, 'numeroto': numeroto}
    )


@login_required
def cliente(request):
    cliente = Cliente.objects.all()
    return render(
        request,
        'cliente.html',
        context={'cliente': cliente}
    )


@login_required
def pedidos(request):
    pedidos = Pedido.objects.filter(carrito__estado='1').order_by('-carrito_id').values('carrito_id', 'carrito__nombre',
                                                                                        'carrito__direccion', 'carrito__celular',
                                                                                        'carrito__fecha', 'carrito__estado').distinct()

    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(pedidos, 10)
        pedidos = paginator.page(page)
    except:
        raise Http404

    return render(
        request,
        'panel/pedidos.html',
        context={'entity': pedidos, 'paginator': paginator}
    )


@login_required
def pedidos_realizados(request):
    pedidos = Pedido.objects.filter(carrito__estado='2').order_by('-carrito_id').values('carrito_id', 'carrito__nombre',
                                                                                        'carrito__direccion', 'carrito__celular', 'carrito__fecha', 'carrito__estado').distinct()
    numerop = Pedido.objects.filter(
        carrito__estado='1').values('carrito').distinct().count()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(pedidos, 10)
        pedidos = paginator.page(page)
    except:
        raise Http404

    return render(
        request,
        'panel/pedidos/pedidos_realizados.html',
        context={'entity': pedidos, 'paginator': paginator, 'numerop': numerop}
    )


@login_required
def estado(request, producto_id):
    estado = Cliente.objects.get(id=producto_id)

    if estado.estado == 1:
        estado.estado = 2
    else:
        estado.estado = 1
    estado.save()
    return redirect('/pedidos/')


@login_required
def productos(request):
    producto = Producto.objects.all()

    return render(
        request,
        'panel/productos.html',
        context={'producto': producto}
    )


@login_required
def stock(request, producto_id):
    stock = Producto.objects.get(id=producto_id)

    if stock.stock == 1:
        stock.stock = 2
    else:
        stock.stock = 1
    stock.save()
    return redirect('/productos/')


@login_required
def agregarp(request):
    if request.method == 'POST':
        producto = Producto(
            producto=request.POST.get('producto'),
            precio=request.POST.get('precio'),
            imagen=request.FILES.get('imagen'),
            categoria_id=request.POST.get('categoria'),
            stock=request.POST.get('stock'),
        )
        producto.save()
        return HttpResponseRedirect('/productos/')
    else:
        producto = ProductoForm()
    return render(request, 'panel/producto/agregardiseño.html', context={'producto': producto})


@login_required
def categoria(request):
    categoria = Categoria.objects.all()
    return render(
        request,
        'panel/categoria/categoria.html',
        context={'categoria': categoria}
    )


@login_required
def categoriap(request):
    if request.method == 'POST':
        categoria = CategoriaForm(request.POST)
        if categoria.is_valid():
            categoria.save()
            return HttpResponseRedirect('/categoria/')
    else:
        categoria = CategoriaForm()
    return render(
        request,
        'panel/categoria/agregar_categoria.html',
        context={'categoria': categoria}
    )


@login_required
def categoriae(request, producto_id):
    form = get_object_or_404(Categoria, id=producto_id)
    if request.method == 'POST':
        modificar = CategoriaForm(request.POST, instance=form)
        if modificar.is_valid():
            modificar.save()
            return HttpResponseRedirect('/categoria/')
    else:
        modificar = CategoriaForm(instance=form)
    return render(
        request,
        'panel/categoria/editar_categoria.html',
        context={'modificar': modificar}
    )


@login_required
def categoria_eliminar(request, producto_id):
    eliminar = get_object_or_404(Categoria, id=producto_id)
    if request.method == 'POST':
        eliminar.delete()
        return HttpResponseRedirect('/categoria/')
    return render(
        request,
        'panel/categoria/eliminar_categoria.html',
        context={'eliminar': eliminar}
    )


@login_required
def detalles(request, producto_id):
    detalles = Pedido.objects.get(id=producto_id)
    carrito = Pedido.objects.filter(carrito=detalles.id)
    total = sum(detalles.subtotal() for detalles in carrito)
    return render(
        request,
        'panel/producto/detalles.html',
        context={'detalles': detalles, 'carrito': carrito, 'total': total}
    )


@login_required
def modificar(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/productos/')
    else:
        form = ProductoForm(instance=producto)
    return render(
        request,
        'panel/producto/modificar.html',
        context={'form': form, 'producto': producto}
    )


@login_required
def informes(request):
    return render(
        request,
        'panel/informes.html'
    )


@login_required
def registro_hoy(request):
    pedidos = Pedido.objects.order_by('-carrito_id').values('carrito_id', 'carrito__nombre',
                                                            'carrito__direccion', 'carrito__celular', 'carrito__fecha').distinct()
    page = request.GET.get('page', 1)
    today = datetime.now()
    registros_hoy = Cliente.objects.filter(fecha_registro__date=today.date())

    try:
        paginator = Paginator(pedidos, 10)
        pedidos = paginator.page(page)
    except:
        raise Http404

    return render(
        request,
        'registros_hoy',
        context={'entity': pedidos, 'paginator': paginator}
    )


@login_required
def ajustes(request):
    usuario = User.objects.all()
    return render(
        request,
        'panel/ajustes.html',
        context={'usuario': usuario}
    )


@login_required
def salir(request):
    logout(request)
    return redirect('/')


@login_required
def pdf(request, producto_id):
    cliente = Cliente.objects.get(id=producto_id)

    pedido = Pedido.objects.filter(carrito=cliente)

    context = {
        'nombre': cliente.nombre,
        'direccion': cliente.direccion,
        'fecha': cliente.fecha,
        'celular': cliente.celular,
        'productos': [],
        'total': 0,
    }

    for pedido in pedido:
        producto = {
            'nombre': pedido.producto.producto,
            'cantidad': pedido.cantidad,
            'precio': pedido.producto.precio,

        }
        producto['subtotal'] = producto['precio'] * \
            producto['cantidad']
        context['productos'].append(producto)
        context['total'] += producto['subtotal']

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="factura.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    pdfmetrics.registerFont(TTFont('Arial', 'Arial.ttf'))

    color = '#0093FF'
    p.saveState()
    p.setFillColor(HexColor(color))
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 680, 'CAZUELAS TORREJAIME')
    p.restoreState()
    p.setFont("Arial", 10)
    p.drawString(50, 660, 'Nit. 1.591.833-1')
    p.drawString(50, 640, 'Direccion: Cl. 7 #18-72, Girardota, Antioquia')
    p.drawString(50, 620, 'Celular: 302 8348422')
    p.drawString(50, 600, 'Email: cazuelastorrejuan@gmail.com')
    imagen = 'productos\static\icono\icono.jpeg'

    x = 100
    y = 700
    width = 100
    height = 100

    imagen = ImageReader(imagen)
    p.drawImage(imagen, x, y, width, height)

    colombia_tz = pytz.timezone('America/Bogota')
    current_time = datetime.datetime.now(colombia_tz)
    context['fecha'] = current_time.strftime('%Y-%m-%d %H:%M:%S')

    p.drawString(50, 570, 'Fecha del pedido: {}'.format(context['fecha']))
    p.drawString(50, 550, 'Nombre: {}'.format(context['nombre']))
    p.drawString(50, 510, 'Celular: {}'.format(context['celular']))
    p.drawString(50, 530, 'Dirección: {}'.format(context['direccion']))

    data = [['                            Producto                               ',
             '   Cantidad   ', '     Precio    ', '       Subtotal       ']]
    for producto in context['productos']:
        nombre = producto['nombre']
        cantidad = producto['cantidad']
        precio = producto['precio']
        subtotal = precio * cantidad

        data.append([nombre, str(cantidad), str(precio), str(subtotal)])

    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1753C9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-0, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]

    table = Table(data)
    table.setStyle(TableStyle(table_style))

    table.wrapOn(p, 100, 200)
    table.drawOn(p, 50, y - 245)

    p.drawString(
        130, 420, '*** Para poder realizar un reclamo o devolución debe de presentar esta factura ***')

    p.setFont("Helvetica-Bold", 12)
    total_formateado = locale.format_string(
        '%.0f', context['total'], grouping=True)
    p.drawString(475, y - 260, 'Total: {}'.format(total_formateado))

    p.showPage()
    p.save()

    return response


@login_required
def tomar_pedidos(request):
    categoria = Categoria.objects.get(categoria='Bebidas')
    productos = Producto.objects.filter(categoria=categoria)
    return render(
        request,
        'panel/tomar_pedidos.html',
        context={'productos': productos}
    )
