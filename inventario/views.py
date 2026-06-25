from urllib import request

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Producto, Movimiento
from datetime import datetime
import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .forms import ProductoForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Credenciales válidas, ahora podemos aplicar reglas de negocio adicionales
            # Ejemplo: restricción horaria (solo para no administradores)
            if not user.groups.filter(name='Admin').exists():  # o según tu lógica de roles
                hora_actual = datetime.now().time()
                hora_inicio = datetime.strptime("08:00", "%H:%M").time()
                hora_fin = datetime.strptime("18:00", "%H:%M").time()
                if not (hora_inicio <= hora_actual <= hora_fin):
                    messages.error(request, "Acceso permitido solo de 08:00 a 18:00 hs.")
                    return redirect('login')

            # Si pasa todas las reglas, inicia sesión
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}.")
            return redirect('dashboard')
        else:
            # Credenciales inválidas
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect('login')

    return render(request, 'inventario/login.html')

@login_required
def dashboard_view(request):
    rol = 'Consulta'
    if request.user.groups.filter(name='Admin').exists():
        rol = 'Admin'
    elif request.user.groups.filter(name='Operador').exists():
        rol = 'Operador'
        
    productos = Producto.objects.all().order_by('id')
    return render(request, 'inventario/dashboard.html', {'productos': productos, 'rol': rol})

@login_required
def registrar_movimiento(request):
    if request.method == 'POST':
        prod_id = request.POST.get('producto_id')
        tipo = request.POST.get('tipo')
        cant = int(request.POST.get('cantidad', 0))
        
        try:
            producto = Producto.objects.get(id=prod_id)
        except Producto.DoesNotExist:
            messages.error(request, f"❌ Error: El producto con ID #{prod_id} no existe.")
            return redirect('dashboard')
            
        if tipo == 'SALIDA' and producto.cantidad < cant:
            messages.error(request, f"❌ Error de Consistencia: Stock insuficiente de '{producto.nombre}'. Disponible: {producto.cantidad} u.")
            return redirect('dashboard')
            
        if tipo == 'ENTRADA':
            producto.cantidad += cant
        elif tipo == 'SALIDA':
            producto.cantidad -= cant
        producto.save()
        
        Movimiento.objects.create(
            producto=producto,
            tipo=tipo,
            cantidad=cant,
            usuario=request.user
        )
        
        messages.success(request, f"✨ Movimiento registrado con éxito para '{producto.nombre}'.")
        return redirect('dashboard')

@login_required
def crear_producto(request):
    if not request.user.groups.filter(name='Admin').exists():
        return HttpResponseForbidden("🛑 Acceso denegado.")
        
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        cantidad_inicial = request.POST.get('cantidad_inicial', 0)
        
        Producto.objects.create(nombre=nombre, precio=precio, cantidad=cantidad_inicial)
        messages.success(request, f"📦 Producto '{nombre}' dado de alta.")
    return redirect('dashboard')

@login_required
def eliminar_producto(request, producto_id):
    if not request.user.groups.filter(name='Admin').exists():
        return HttpResponseForbidden("🛑 Acceso denegado.")
        
    try:
        producto = Producto.objects.get(id=producto_id)
        nombre_prod = producto.nombre
        producto.delete()
        messages.success(request, f"🗑️ El producto '{nombre_prod}' fue eliminado.")
    except Producto.DoesNotExist:
        messages.error(request, "❌ El producto no existe.")
        
    return redirect('dashboard')


@login_required
def editar_producto(request, producto_id):
    # Solo administradores
    if not request.user.groups.filter(name='Admin').exists():
        return HttpResponseForbidden("🛑 Acceso denegado. Solo administradores pueden editar productos.")

    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"✏️ Producto '{producto.nombre}' actualizado correctamente.")
            return redirect('dashboard')  # O la vista que lista los productos
    else:
        form = ProductoForm(instance=producto)
    if request.user.groups.filter(name='Admin').exists():
            rol = 'Admin'
    elif request.user.groups.filter(name='Operador').exists():
            rol = 'Operador'
    else:
            rol = 'Consulta'

    return render(request, 'inventario/editar_producto.html', {
            'form': form,
            'producto': producto,
            'rol': rol,      
        })

@login_required
def exportar_csv(request):
    es_admin = request.user.groups.filter(name='Admin').exists()
    es_consulta = request.user.groups.filter(name='Consulta').exists()
    
    if not (es_admin or es_consulta):
        return HttpResponseForbidden("🛑 No autorizado.")
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventario_actual.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Producto', 'Stock Disponible', 'Precio Unitario'])
    
    productos = Producto.objects.all().order_by('id')
    for p in productos:
        writer.writerow([p.id, p.nombre, p.cantidad, p.precio])
        
    return response

def logout_view(request):
    logout(request)
    return redirect('login')
