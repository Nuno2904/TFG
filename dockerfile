#archivo de instrucciones para construir una imagen de Docker para una aplciación de fastapi.
#Dockerfile → Imagen → Contenedor

#empieza desde una imagen base de python 3.11 slim, que es una versión ligera de python.
FROM python:3.11-slim 

#por qué usar /app
#Evita conflictos: app está separado del sistema de archivos del contenedor (que tiene /usr, /etc, /var, etc.). Si accidentalmente sobrescribes algo, no afectas el SO.
#Claridad: Cualquiera que lea tu Dockerfile sabe que app contiene la aplicación. Es un estándar que todos los developers entienden.
#Seguridad: Más aislado que usar root / o directorios del sistema.
#Facilita debugging: Si entras al contenedor con docker exec -it, sabes exactamente dónde está tu código.
WORKDIR /app

#copiar los archivos de dependencia al contendor para saber que tiene que instalar.
COPY requirements.txt .
COPY pyproject.toml .

RUN pip install --no-cache-dir -r requirements.txt

#copia todo el codigo de backend TFG al contenedor para que pueda ejecutarse dentro del contenedor.
COPY . .

EXPOSE 8000

#cuadno inicie el contendeor, ejecuta el comando uvicorn con host 0.0.0.0 para que pueda aer cualquiera y lo corre en el puerto 8000, 
#que es el puerto que expusimos antes. Esto inicia la aplicación de FastAPI dentro del contenedor.
#no se usa make , porque la imagen no lo tiene instalado y no es necesario para ejecutar la aplicacion, si no habríaque poner que se descargue.


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]