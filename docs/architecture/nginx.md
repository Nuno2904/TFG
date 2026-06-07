# Nginx — Proxy inverso en TimeSeriesLab

## Qué es Nginx

Nginx es un servidor web de código abierto que actúa como intermediario entre el usuario y los servicios que corren en el servidor. Cuando alguien escribe una dirección en el navegador y pulsa enter, la petición viaja por internet hasta el servidor, pero alguien tiene que recibirla y decidir qué hacer con ella. Ese es el trabajo de Nginx.

Su función más habitual es la de **proxy inverso**: recibe todas las peticiones entrantes por un único punto de entrada (el puerto 80, que es el puerto estándar de HTTP en internet) y las redirige internamente al servicio correspondiente según la ruta solicitada. El usuario no sabe que existe este intermediario; desde su perspectiva, simplemente está accediendo a una dirección web normal.

Nginx destaca por su alto rendimiento bajo carga elevada, su bajo consumo de recursos y su capacidad para gestionar miles de conexiones simultáneas de forma eficiente, lo que lo convierte en uno de los servidores web más utilizados en entornos de producción a nivel mundial.

---

## El problema que resuelve en este proyecto

En TimeSeriesLab coexisten dos servicios diferenciados dentro del mismo servidor:

- El **frontend** React, que es la interfaz web que el usuario ve y con la que interactúa
- El **backend** FastAPI, que es la API REST que contiene toda la lógica de negocio y los modelos de machine learning

Ambos servicios son independientes y corren en contenedores Docker separados. El problema es que el usuario accede al servidor a través de una única dirección IP, por ejemplo `http://161.35.40.XX`. Alguien tiene que recibir esa petición y decidir si debe ir al frontend o al backend. Ese es exactamente el papel que cumple Nginx en este proyecto.

---

## Cómo funciona en este proyecto concretamente

Nginx actúa como árbitro mirando la ruta de cada petición entrante:

- Si el usuario abre el navegador y accede a `http://161.35.40.XX` → Nginx sirve directamente la interfaz React
- Si el usuario pulsa un botón en la interfaz que internamente genera una llamada a `http://161.35.40.XX/api/v1/...` → Nginx detecta que la ruta empieza por `/api/` y redirige la petición al contenedor del backend FastAPI

El flujo completo de una acción típica, como iniciar sesión, sería el siguiente:

1. El usuario introduce sus credenciales en la interfaz y pulsa "Entrar"
2. React genera una petición HTTP a `http://161.35.40.XX/api/v1/auth/login`
3. Nginx recibe esa petición, detecta el prefijo `/api/` y la redirige internamente al contenedor de FastAPI
4. FastAPI valida las credenciales consultando PostgreSQL y genera un token JWT
5. La respuesta vuelve a través de Nginx hasta el navegador del usuario
6. React recibe el token y lo almacena para las siguientes peticiones

Todo esto ocurre de forma completamente transparente para el usuario, que únicamente ve la interfaz y no percibe que por detrás hay tres contenedores distintos comunicándose entre sí.

---

## Por qué Nginx y no una comunicación directa entre frontend y backend

La alternativa más inmediata sería exponer cada servicio en un puerto distinto y que el frontend llamase directamente al backend:

- `http://161.35.40.XX:3000` → frontend React
- `http://161.35.40.XX:8000` → backend FastAPI

Esta estructura funciona perfectamente en un entorno de desarrollo local, pero en producción genera problemas importantes:

### Problema 1 — CORS

Cuando React sirviéndose desde el puerto 3000 intenta hacer una petición al puerto 8000, el navegador lo interpreta como una llamada a un origen distinto y la bloquea por seguridad. Este mecanismo de protección del navegador se llama CORS (*Cross-Origin Resource Sharing*). Para evitarlo habría que configurar el backend con excepciones explícitas que permitan peticiones desde el puerto 3000, lo que añade complejidad y, si se configura de forma demasiado permisiva, puede suponer un riesgo de seguridad.

Con Nginx ambos servicios comparten el mismo origen desde la perspectiva del navegador. El frontend y la API viven bajo la misma dirección y el mismo puerto, por lo que el navegador no detecta ningún cruce de origen y el problema desaparece por completo.

### Problema 2 — Exposición innecesaria de puertos

Tener el puerto 8000 abierto públicamente significa que cualquier persona en internet puede llamar directamente a los endpoints de la API sin pasar por ningún filtro ni capa de control. Esto representa una superficie de ataque innecesaria.

Con Nginx únicamente el puerto 80 está expuesto al exterior. El backend FastAPI y la base de datos PostgreSQL permanecen dentro de la red interna de Docker, completamente inaccesibles desde el exterior salvo a través del proxy. Esto reduce significativamente la exposición del sistema.

### Problema 3 — Experiencia de usuario y URLs limpias

Con la estructura de puertos separados el usuario tendría que conocer en qué puerto está cada servicio, o la aplicación tendría que gestionar URLs distintas con puertos explícitos. Con Nginx todo vive bajo una única dirección limpia sin puertos visibles, como cualquier sitio web convencional.

---

## Resumen

| | Sin Nginx (puertos separados) | Con Nginx |
|---|---|---|
| Punto de entrada | Dos puertos distintos | Un único puerto (80) |
| CORS | Requiere configuración explícita | No hay cruce de origen |
| Seguridad | Backend expuesto públicamente | Backend inaccesible desde exterior |
| URL para el usuario | `IP:3000` y `IP:8000` | Una sola dirección limpia |
| Complejidad de despliegue | Mayor | Centralizada en Nginx |

En definitiva, Nginx no es un componente imprescindible para que la aplicación funcione en local, pero sí lo es para que funcione de forma segura, limpia y profesional en un entorno de producción real accesible desde internet.
