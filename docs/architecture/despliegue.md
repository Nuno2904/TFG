# Infraestructura de despliegue — Docker, Nginx y PostgreSQL

## Visión general

En producción, TimeSeriesLab no se ejecuta como un único programa sino como un conjunto de tres servicios independientes que colaboran entre sí. Cada servicio corre dentro de su propio **contenedor Docker**, aislado del resto del sistema, y Nginx actúa como punto de entrada único que recibe todas las peticiones del exterior y las distribuye correctamente.

```
USUARIO (navegador)
        │
        ▼
    [ NGINX ]  ← único punto de entrada (puerto 81)
     /      \
    /        \
   ▼          ▼
[FRONTEND] [BACKEND FastAPI]
  React         │
             [POSTGRESQL]
```

---

## Docker — qué es y por qué se usa

Docker es una herramienta que permite empaquetar una aplicación junto con todo lo que necesita para funcionar (dependencias, librerías, configuración) en una unidad llamada **contenedor**. Un contenedor es un entorno aislado y reproducible: funciona igual en cualquier máquina independientemente de lo que tenga instalado el sistema operativo anfitrión.

Esto resuelve uno de los problemas más clásicos del despliegue de software: *"en mi máquina funciona"*. Al empaquetar la aplicación en un contenedor, se garantiza que el entorno de producción es idéntico al de desarrollo.

En este proyecto se utilizan tres contenedores, uno por cada servicio:

| Contenedor | Imagen | Función |
|---|---|---|
| `tfg-nginx` | nginx:1.27-alpine | Proxy inverso y servidor del frontend |
| `tfg-backend` | tfg-backend (imagen propia) | API REST con FastAPI |
| `tfg-postgres` | postgres:15-alpine | Base de datos PostgreSQL |

Los tres contenedores se definen y orquestan mediante **Docker Compose**, que permite levantarlos todos con un único comando (`docker compose up -d --build`) y gestiona automáticamente la red interna que los comunica entre sí.

---

## Los tres contenedores en detalle

### tfg-postgres — La base de datos

PostgreSQL corre en su propio contenedor y almacena todos los datos persistentes de la aplicación: usuarios registrados, datasets subidos y modelos entrenados.

La característica más importante de este contenedor es que sus datos **sobreviven a los reinicios**. Esto se consigue mediante un **volumen Docker**: una carpeta especial que Docker mantiene fuera del contenedor, en el sistema de archivos real del VPS. Cuando PostgreSQL escribe datos, no los guarda dentro del contenedor sino en ese volumen externo.

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

Esta línea del `docker-compose.yml` le indica a Docker que todo lo que PostgreSQL escriba en su carpeta de datos interna (`/var/lib/postgresql/data`) se almacene en realidad en el volumen `postgres_data`, que existe de forma independiente al contenedor.

El resultado es que el contenedor es prescindible pero los datos no. Si el contenedor de PostgreSQL se para, se borra o se reconstruye, el volumen con todos los datos permanece intacto en el VPS. Al levantar el contenedor de nuevo, PostgreSQL encuentra sus datos exactamente donde los dejó.

Esto explica lo que se observa al ejecutar `docker ps`:

```
tfg-postgres   Up 26 hours    ← lleva 26 horas con datos
tfg-backend    Up 32 seconds  ← acaba de reconstruirse
tfg-nginx      Up 26 seconds  ← acaba de reconstruirse
```

El backend y Nginx se reconstruyeron para desplegar cambios, pero PostgreSQL ni se tocó. Sus datos se mantuvieron intactos durante todo el proceso.

### tfg-backend — La API FastAPI

El backend es la imagen Docker construida a partir del código del proyecto. Contiene Python, todas las dependencias del `requirements.txt`, los módulos de machine learning (Prophet, pmdarima, statsmodels) y la lógica de la aplicación.

Cuando arranca, se conecta a `tfg-postgres` a través de la red interna de Docker usando el nombre del contenedor como hostname. Desde el backend, la base de datos es simplemente `postgres://tfg-postgres:5432/tfg_db`, sin necesidad de conocer ninguna IP real.

El backend no está expuesto directamente al exterior. Solo es accesible desde dentro de la red Docker, lo que significa que ningún usuario externo puede llamar a la API directamente sin pasar por Nginx.

### tfg-nginx — El proxy inverso

Nginx es el único contenedor que está expuesto al exterior, escuchando en el puerto 81 del VPS. Actúa como puerta de entrada única y decide a dónde va cada petición según su ruta.

Su configuración establece dos reglas:

- Las peticiones que comienzan por `/api/` → se redirigen internamente a `tfg-backend:8000`
- El resto de peticiones → Nginx sirve directamente los ficheros estáticos del frontend React

Nginx también se encarga de servir el frontend. Los ficheros compilados de React (HTML, CSS, JavaScript) se copian dentro del contenedor de Nginx durante la construcción, por lo que no hace falta un contenedor separado para el frontend.

---

## El flujo completo de una petición

Para entender cómo encajan todas las piezas, se puede seguir el recorrido completo de una acción típica: el usuario inicia sesión.

```
1. El usuario escribe http://161.35.40.XX:81 en el navegador
        │
        ▼
2. Nginx recibe la petición → no empieza por /api/ → sirve index.html de React
        │
        ▼
3. React se carga en el navegador del usuario
        │
        ▼
4. El usuario introduce email y contraseña y pulsa "Entrar"
        │
        ▼
5. React genera POST http://161.35.40.XX:81/api/v1/auth/login
        │
        ▼
6. Nginx recibe la petición → empieza por /api/ → la redirige a tfg-backend:8000
        │
        ▼
7. FastAPI valida las credenciales consultando tfg-postgres
        │
        ▼
8. PostgreSQL devuelve los datos del usuario a FastAPI
        │
        ▼
9. FastAPI genera el token JWT y devuelve la respuesta a Nginx
        │
        ▼
10. Nginx devuelve la respuesta al navegador del usuario
        │
        ▼
11. React recibe el token, lo guarda en sessionStorage y redirige al dashboard
```

En ningún momento el usuario percibe que hay tres contenedores distintos comunicándose. Todo ocurre bajo una única dirección y de forma completamente transparente.

---

## Por qué esta arquitectura y no una más simple

La alternativa directa sería exponer el backend en un puerto y que el frontend lo llamase directamente, sin Nginx de por medio. Esto genera tres problemas en producción:

**CORS.** Cuando el frontend en el puerto 3000 llama al backend en el puerto 8000, el navegador lo detecta como dos orígenes distintos y bloquea la petición por seguridad. Con Nginx todo sale del mismo origen y el problema desaparece.

**Seguridad.** Sin Nginx, el backend estaría expuesto públicamente en su puerto. Cualquier persona podría llamar a los endpoints de la API directamente. Con Nginx el backend es inaccesible desde el exterior: solo recibe peticiones que Nginx le reenvía.

**Simplicidad para el usuario.** Con puertos separados el usuario tendría que conocer en qué puerto está cada servicio. Con Nginx todo vive bajo una única dirección limpia.

---

## Resumen

| Componente | Rol | Accesible desde exterior |
|---|---|---|
| Nginx | Punto de entrada único, proxy inverso, servidor del frontend | Sí (puerto 81) |
| FastAPI | Lógica de negocio y API REST | No (solo red interna Docker) |
| PostgreSQL | Persistencia de datos | No (solo red interna Docker) |

La arquitectura garantiza que solo Nginx está expuesto al exterior, mientras que el backend y la base de datos permanecen protegidos dentro de la red interna de Docker, accesibles únicamente a través del proxy.
