# Tiendify API

API REST de una tienda. Administra usuarios por rol, catálogo de productos, ventas con descuento de stock, gastos y el saldo de caja. Está hecha con Django y Django REST Framework, y la consume un cliente en Angular (`http://localhost:4200`).

## Stack

| Pieza | Versión / detalle |
| --- | --- |
| Python | 3.10 o superior (el proyecto usa Django 5) |
| Django | 5.0.2 |
| Django REST Framework | 3.14 |
| Base de datos | MySQL (`proyecto_tiendify_db`) |
| Autenticación | Token de DRF, enviado como `Authorization: Bearer <token>` |
| CORS | `django-cors-headers`, origen `http://localhost:4200` |

## Qué hace

- Da de alta, lista, edita y elimina tres perfiles: administrador, master y trabajador. Cada uno es un usuario de Django más una ficha con datos propios.
- Inicia sesión y devuelve el perfil según el rol, junto con el token.
- Mantiene el catálogo (clave, nombre, precio, stock, categoría, contenido y unidad).
- Registra una venta y resta el stock dentro de una transacción. Si no hay existencia, responde `409`.
- Registra gastos y calcula ventas, IVA y utilidad en un rango de fechas.
- Resume la caja: ventas, ingresos directos, gastos y retiros.

## Roles

El usuario se crea con el correo como `username`. El campo `rol` se guarda como grupo de Django. En el login solo se toma el primer grupo.

| Rol | Grupo | Login en `POST /token/` |
| --- | --- | --- |
| Administrador | `administrador` | Datos del usuario, `token` y `rol` |
| Master | `master` | Ficha de master, `token` y `rol` |
| Trabajador | `trabajador` | Ficha de trabajador, `token` y `rol` |

Cualquier otro grupo responde `403`.

## Puesta en marcha

1. Crea la base en MySQL:

```sql
CREATE DATABASE proyecto_tiendify_db CHARACTER SET utf8mb4;
```

2. Revisa `my.cnf` en la raíz. Ahí está el host, el puerto, el nombre de la base y el usuario. La contraseña se deja vacía en el archivo de ejemplo.

3. Instala y arranca (Windows):

```bat
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

La API queda en `http://127.0.0.1:8000/`.

`ALLOWED_HOSTS` solo incluye `127.0.0.1`. `settings.py` lee la conexión desde `my.cnf`.

## Autenticación

```http
POST /token/
Content-Type: application/json

{
  "username": "ana@tienda.local",
  "password": "una-clave"
}
```

`username` es el correo con el que se registró la persona.

Las rutas marcadas como autenticadas esperan:

```http
Authorization: Bearer <token>
```

`GET /logout/` borra ese token. Requiere sesión iniciada.

## Rutas

La base es `http://127.0.0.1:8000`. Las fechas de filtro usan `YYYY-MM-DD`.

### Sistema y sesión

| Método | Ruta | Auth | Qué hace |
| --- | --- | --- | --- |
| GET | `/bootstrap/version` | No | Responde `{ "version": "1.0.0" }` |
| POST | `/token/` | No | Login. Devuelve perfil, `token` y `rol` |
| GET | `/logout/` | Sí | Invalida el token |

### Administradores

Alta pública. Listar, editar, borrar y el conteo de usuarios exigen token.

| Método | Ruta | Auth | Qué hace |
| --- | --- | --- | --- |
| GET | `/admin/?id=` | No | Ficha de un administrador |
| POST | `/admin/` | No | Crea usuario y ficha |
| GET | `/lista-admins/` | Sí | Lista administradores activos |
| GET | `/admins-edit/` | Sí | Totales de admins, masters y trabajadores |
| PUT | `/admins-edit/` | Sí | Actualiza ficha y nombre |
| DELETE | `/admins-edit/?id=` | Sí | Elimina el usuario (y la ficha en cascada) |

Cuerpo del alta:

```json
{
  "rol": "administrador",
  "first_name": "Ana",
  "last_name": "López",
  "email": "ana@tienda.local",
  "password": "una-clave",
  "clave_admin": "ADM-01",
  "telefono": "2710000000",
  "rfc": "LOPA800101XXX",
  "edad": 30
}
```

Respuesta `201`: `{ "admin_created_id": 1 }`. Si el correo ya existe, `400`.

### Trabajadores

Misma forma que los administradores. `rol` debe ser `trabajador` y la clave se llama `clave_trabajador`.

| Método | Ruta | Auth |
| --- | --- | --- |
| GET | `/trabajadores/?id=` | No |
| POST | `/trabajadores/` | No |
| GET | `/lista-trabajadores/` | Sí |
| PUT | `/trabajadores-edit/` | Sí |
| DELETE | `/trabajadores-edit/?id=` | Sí |

El alta responde `{ "trabajador_created_id": 1 }`.

### Masters

| Método | Ruta | Auth |
| --- | --- | --- |
| GET | `/master/?id=` | No |
| POST | `/master/` | No |
| GET | `/lista-master/` | Sí |
| PUT | `/master-edit/` | Sí |
| DELETE | `/master-edit/?id=` | Sí |

El alta pide `clave_master`, `telefono` y `rfc`. Responde `{ "master_created_id": 1 }`.

### Productos

Estas rutas no piden token.

| Método | Ruta | Qué hace |
| --- | --- | --- |
| GET | `/products/?q=` | Lista. `q` busca en nombre y clave |
| POST | `/products/` | Crea un producto (`201`) |
| GET | `/product/?id=` | Uno por id |
| PUT | `/products-edit/` | Edición parcial. El cuerpo incluye `id` |
| DELETE | `/products-edit/?id=` | Elimina el producto |

Cuerpo de alta:

```json
{
  "clave": "LEC-01",
  "nombre": "Leche 1 L",
  "precio": "24.50",
  "stock": 40,
  "categoria": "Abarrotes",
  "contenido": "1.00",
  "unidad": "L"
}
```

`clave` es única.

### Ventas

`POST /ventas/` no pide token. `GET /lista-ventas/` sí.

```json
{
  "subtotal": "100.00",
  "iva": "16.00",
  "total": "116.00",
  "recibido": "200.00",
  "cambio": "84.00",
  "items": [
    { "producto_id": 1, "cantidad": 2, "precio_unit": "50.00" }
  ]
}
```

Si un producto no existe, responde `400`. Si el stock no alcanza, `409` con `producto_id` y `stock`. Si sale bien, `201` con `venta_id`, y el stock baja en la misma transacción.

`GET /lista-ventas/?q=` filtra por total cuando `q` es numérico. Ordena de la más reciente a la más antigua.

### Gastos

Todas piden token.

| Método | Ruta | Qué hace |
| --- | --- | --- |
| POST | `/gastos/` | Crea. Campos: `monto`, `tipo`, `nombre`, `notas` |
| GET | `/lista-gastos/` | Lista. Filtros: `q`, `tipo`, `start`, `end` |
| PUT | `/gastos-edit/?id=` | Edición parcial |
| DELETE | `/gastos-edit/?id=` | Elimina. Responde `204` |

### Estadísticas

Ambas piden token. `start` y `end` son opcionales.

| Método | Ruta | Respuesta |
| --- | --- | --- |
| GET | `/stats-ventas/` | `sin_iva`, `iva`, `con_iva` y el rango |
| GET | `/stats-ingresos-egresos/` | Ventas, `egresos` y `utilidad_neta` (`ventas_con_iva - egresos`) |

### Caja

Todas piden token.

| Método | Ruta | Qué hace |
| --- | --- | --- |
| GET | `/caja/resumen/` | `vendido`, `gastado`, `ingresos_directos`, `retiros` y `saldo` |
| POST | `/caja/ingreso/` | Registra un ingreso. Cuerpo: `monto` y `nota`. El tipo siempre queda `INGRESO` |
| GET | `/lista-ingresos/` | Ingresos. Filtros: `q`, `start`, `end` |

El saldo es ventas + ingresos directos − gastos − retiros.

## Modelo

```text
User (Django)
 ├── Administradores   clave_admin, teléfono, rfc, edad
 ├── Trabajadores      clave_trabajador, rfc, edad, teléfono
 ├── Master            clave_master, teléfono, rfc, edad
 └── Limpieza          teléfono, rfc, edad   (tabla creada, sin rutas)

Producto
 └── VentaDetalle ── Venta   subtotal, iva, total, recibido, cambio, fecha

Gasto            monto, tipo, nombre, notas, fecha
CajaMovimiento   monto, tipo (INGRESO | RETIRO), nota, fecha
```

## Estructura

```text
manage.py
main.py                      punto de entrada WSGI para App Engine
app.yaml                     servicio default en App Engine
my.cnf                       conexión a MySQL
requirements.txt
proyecto_tiendify_api/
  models.py                  modelos y BearerTokenAuthentication
  urls.py                    rutas
  serializers.py
  settings.py
  views/                     auth, usuarios, productos, ventas, gastos, stats, caja
  migrations/
static/                      archivos de admin y de DRF
```

## Notas

- `PAGE_SIZE` está en 10, pero las vistas propias devuelven la lista completa.
- El alta de administrador, trabajador, master y las lecturas `GET` por id no piden token. Tampoco el catálogo ni el registro de ventas.
- `MasterViewEdit` llama a `get_object_or_404(master, ...)` con un nombre que no es el modelo. Editar o borrar un master falla hasta que eso apunte a `Master`.
- El modelo `Limpieza` existe por la migración `0015` y no tiene endpoints.
- `deploy.sh` publica en App Engine con el proyecto `pik-api`. `app.yaml` declara el runtime `python37`, anterior a Django 5.
