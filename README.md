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



## Endpoints



## Documentación



## Notas

- El sistema cuenta con usuarios creados en la base de datos para facilitar la prueba. Para proceder desde cero se debe crear un superusuario:
 ```
 python manage.py createsuperuser
 ```
 y luego desde la siguente pantalla:
 ```
 http://127.0.0.1:8000/admin/
 ```
 se puede proceder a crear usuarios y añadirlos al grupo de su rol correspondiente.

