# Sistema de Gestión de Stock e Inventario Seguro

Esta aplicación web permite centralizar el control de existencias, automatizar el cálculo de stock disponible, registrar los movimientos físicos de mercadería y auditar en tiempo real qué usuario realizó cada operación para evitar desvíos o pérdidas de información.

Equipo: Juan Cruz Novoa, Nicolas Dario Pagano Millan, Diego Prieto, Alejandro Piris y Agustin Miguelez.

## Stack tecnologico

- Backend: Django
- Autenticación: Sistema de autenticación integrado de django (django.contrib.auth)
- Base de datos: SQLite
- Frontend: HTML5, CSS3, Bootstrap

## Instalación

### 1. Clonar el repositorio

```
git clone https://github.com/diego1321/TP-final-Backend.git
cd TP-final-Backend
```
### 2. Instalar las dependencias

```
pip install -r requirements.txt
```

### 3. Levantar el servidor

```
python manage.py runserver
```

## Usuarios

El sistema funciona bajo un esquema de control de acceso basado en roles:

- Administrador (Admin): Posee control total del ecosistema. Puede dar de alta nuevos productos en el catálogo, registrar movimientos de entrada/salida de stock, visualizar alertas del sistema y exportar reportes consolidados.
- Operador: Perfil técnico encargado de las tareas de almacén. Puede listar el inventario actual y registrar movimientos de stock (entradas y salidas), pero tiene estrictamente denegada la creación de nuevos productos.
- Consulta: Perfil de auditoría o gerencia. Puede visualizar el estado del inventario actual y exportar reportes en CSV, pero no puede alterar ninguna base de datos ni registrar movimientos.


## Modelo de datos

### Producto

| Campo | Tipo de dato | Descripción |
|-------|--------------|-------------|
| id | AutoField | Identificador único del producto (generado automáticamente por Django). |
| nombre | CharField (max_length=100) | Nombre del producto. |
| cantidad | IntegerField | Cantidad disponible en stock. |
| precio | DecimalField (max_digits=10, decimal_places=2) | Precio unitario del producto. |

### Movimiento

| Campo | Tipo de dato | Descripción |
|-------|--------------|-------------|
| id | AutoField | Identificador único del movimiento (generado automáticamente por Django). |
| producto | ForeignKey → Producto | Producto asociado al movimiento. |
| tipo | CharField | Tipo de movimiento: **ENTRADA** o **SALIDA**. |
| cantidad | IntegerField | Cantidad de unidades ingresadas o retiradas. |
| fecha | DateTimeField | Fecha y hora del movimiento (generada automáticamente). |
| usuario | ForeignKey → User | Usuario que registró el movimiento. |

## Endpoints

| Método | Endpoint | Vista | Descripción |
|--------|----------|-------|-------------|
| GET | `/admin/` | Django Admin | Panel de administración de Django. |
| GET | `/` | `dashboard_view` | Muestra el dashboard con el listado de productos. |
| GET / POST | `/login/` | `login_view` | Inicio de sesión de usuarios. |
| GET | `/logout/` | `logout_view` | Cierra la sesión del usuario. |
| POST | `/movimiento/` | `registrar_movimiento` | Registra una entrada o salida de stock. |
| GET | `/exportar/` | `exportar_csv` | Exporta el stock en formato CSV. |
| POST | `/crear-producto/` | `crear_producto` | Alta de un nuevo producto. |
| POST | `/eliminar-producto/<int:producto_id>/` | `eliminar_producto` | Elimina un producto por ID. |
| GET / POST | `/editar-producto/<int:producto_id>/` | `editar_producto` | Edita la información de un producto existente. |
| GET | `/exportar-movimientos/` | `exportar_csv_movimientos` | Exporta el historial de movimientos del inventario en formato CSV. |

## Documentación



## Notas

1.  El sistema cuenta con una base de datos (db.sqlite3) que contiene usuarios de cada rol y productos cargados para poder facilitar el testeo. Para proceder desde cero se debe crear un superusuario:
 ```
 python manage.py createsuperuser
 ```
 y luego desde la siguente pantalla:
 ```
 http://127.0.0.1:8000/admin/
 ```
se crean los usuarios y se añaden al grupo de su rol correspondiente. Con eso ya se puede logear y utilizar la aplicación.


