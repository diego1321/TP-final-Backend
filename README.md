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

### Categoria

| Campo | Tipo de dato  | Descripción |
| ------------ | ------------ | ------------ |
|id  | AutoField | Identificador único de la categoria (generado automáticamente por Django).
|  nombre | CharField(max_length=100)  | Nombre de la categoria.  |
| descripcion  | TextField  | Descripción de la categoria |

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
| compra | ForeignKey → Compra | Identificación de la compra. |
| venta | ForeignKey → Venta | Identificación de la venta. |

### Proveedor

| Campo  | Tipo de dato  | Descripción  |
| ------------ | ------------ | ------------ |
|id  | AutoField | Identificador único del proveedor (generado automáticamente por Django).
| nombre  | CharField(max_length=100)  | Nombre del proveedor.  |
|  cuit | CharField(max_length=20)  | Cuit del proveedor.  |
|  telefono | CharField(max_length=50)  | Telefono del proveedor.  |
|  email | EmailField  | Correo electronico del proveedor.  |

### Cliente

| Campo  | Tipo de dato  | Descripción  |
| ------------ | ------------ | ------------ |
| id | AutoField | Identificador único del cliente (generado automáticamente por Django).
| nombre  | CharField(max_length=100)  | Nombre del cliente.  |
|  dni_cuit | CharField(max_length=20)  | Dni o cuit del cliente.  |
|  email | EmailField  | Correo electronico del cliente.  |

### Compra

| Campo  | Tipo de dato  | Descripción  |
| ------------ | ------------ | ------------ |
| id | AutoField | Identificador único de la compra (generado automáticamente por Django).
| proveedor  | ForeignKey → Proveedor  | Nombre del proveedor a quien se le adquieren los productos.  |
|  fecha | DateTimeField  | Fecha en la que se realiza la compra.  |
|  total | DecimalField(max_digits=12, decimal_places=2  | Monto total de la compra.  |
|  usuario | ForeignKey → User  | Usuario (admin u operario) que registra la compra en el sistema.  |

### Venta

| Campo  | Tipo de dato  | Descripción  |
| ------------ | ------------ | ------------ |
| id | AutoField | Identificador único de la compra (generado automáticamente por Django).
| cliente  | ForeignKey → Cliente  | Nombre del cliente que adquiere los productos.  |
|  fecha | DateTimeField  | Fecha en la que se realiza la venta.  |
|  total | DecimalField(max_digits=12, decimal_places=2)  | Monto total de la venta.  |
|  usuario | ForeignKey → User  | Usuario (admin u operario) que registra la venta en el sistema.  |

### DetalleCompra

| Campo | Tipo | Descripción |
|--------|------|-------------|
| compra | ForeignKey → Compra | Compra a la que pertenece el detalle. |
| producto | ForeignKey → Producto | Producto adquirido. |
| cantidad | PositiveIntegerField | Cantidad comprada del producto. |
| precio_unitario | DecimalField | Precio unitario del producto al momento de la compra. |

### DetalleVenta

| Campo | Tipo | Descripción |
|--------|------|-------------|
| venta | ForeignKey → Venta | Venta a la que pertenece el detalle. |
| producto | ForeignKey → Producto | Producto vendido. |
| cantidad | PositiveIntegerField | Cantidad vendida del producto. |
| precio_unitario | DecimalField | Precio unitario del producto al momento de la venta. |

## Endpoints


### Inventario

| Método | Endpoint | Descripción |
|---------|----------|-------------|
| GET / POST | `/inventario/login/` | Inicio de sesión de usuarios.. |
| GET / POST | `/inventario/logout/` | Cierre de sesión del usuario. |
| GET | `/inventario/` | Muestra el dashboard principal del sistema. |
| GET / POST | `/inventario/productos/crear/` | Crea un nuevo producto. |
| GET / POST | `/inventario/productos/<id>/editar/` | Edita un producto existente. |
| GET / POST | `/inventario/productos/<id>/eliminar/` | Realiza la baja lógica de un producto. |
| GET / POST | `/inventario/movimientos/registrar/` | Registra manualmente un movimiento de stock. |
| GET | `/inventario/productos/top/` | Muestra el ranking de productos más vendidos. |
| GET | `/inventario/exportar/productos/` | Exporta el listado de productos a CSV. |
| GET | `/inventario/exportar/movimientos/` | Exporta el historial de movimientos a CSV. |

### Compras

| Método | Endpoint | Descripción |
|---------|----------|-------------|
| GET / POST | `/compras/simular/` | Registra una nueva compra con múltiples productos. |
| GET | `/compras/historico/` | Muestra el historial de compras. |
| GET | `/compras/detalle/<compra_id>/` | Muestra el detalle de una compra específica. |
| GET / POST | `/compras/proveedor/nuevo/` | Registra un nuevo proveedor. |

### Ventas

| Método | Endpoint | Descripción |
|---------|----------|-------------|
| GET / POST | `/ventas/simular/venta/` | Registra una nueva venta con múltiples productos. |
| GET | `/ventas/historico/ventas/` | Muestra el historial de ventas. |
| GET | `/ventas/detalle/<venta_id>/` | Muestra el detalle de una venta específica. |
| GET / POST | `/ventas/cliente/nuevo/` | Registra un nuevo cliente. |
| GET | `/ventas/ticket/pdf/<tipo>/<id>/` | Genera y descarga el ticket de compra o venta en formato PDF. |

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


