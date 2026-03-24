# Setup del servidor y despliegue con Docker

Este documento asume un servidor limpio con Ubuntu 22.04/24.04 o Debian 12, acceso por SSH y un usuario con permisos `sudo`.

El despliegue deja disponible:

- Frontend + nginx: `http://IP_DEL_SERVIDOR/`
- API healthcheck: `http://IP_DEL_SERVIDOR/health`
- Swagger: `http://IP_DEL_SERVIDOR/docs`

## 1. Entrar al servidor

Desde tu equipo local:

```bash
ssh usuario@IP_DEL_SERVIDOR
```

## 2. Actualizar paquetes e instalar utilidades básicas

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg git ufw openssl
```

## 3. Instalar Docker Engine y Docker Compose Plugin

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

Comprobar instalación:

```bash
docker --version
docker compose version
```

## 4. Configurar firewall

Si el servidor usa `ufw`, abre solo lo necesario:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

Nota:

- Ahora mismo el `docker-compose.yml` también publica PostgreSQL en `5432`.
- Si el servidor va a estar expuesto a Internet, no conviene dejar ese puerto abierto públicamente salvo que lo necesites.
- Si no vas a conectarte a PostgreSQL desde fuera del servidor, no abras `5432` en el firewall.

## 5. Clonar el repositorio

Si el repositorio es público:

```bash
cd /opt
sudo git clone URL_DEL_REPO tfg
sudo chown -R $USER:$USER /opt/tfg
cd /opt/tfg
```

Si el repositorio es privado, usa una de estas opciones:

- `git clone` con token personal
- subir el proyecto por `scp` o `rsync`
- desplegar una clave SSH en el servidor y usar la URL SSH del repo

## 6. Crear el archivo `.env`

Si existe plantilla:

```bash
cp .env.example .env
```

Genera una clave segura:

```bash
openssl rand -hex 32
```

Edita el archivo:

```bash
nano .env
```

Contenido recomendado para este despliegue:

```env
DB_USER=tfg_user
DB_PASSWORD=CAMBIA_ESTA_PASSWORD
DB_NAME=tfg_db

SECRET_KEY=PEGA_AQUI_LA_CLAVE_GENERADA
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

APP_NAME=TFG API
APP_VERSION=1.0.0
DEBUG=false
```

Importante:

- No hace falta poner `DATABASE_URL` para Docker si vas a usar el `docker-compose.yml` actual, porque el servicio `backend` ya la construye internamente apuntando a `db`.
- No reutilices la `.env` local de desarrollo si contiene credenciales de `localhost` o valores inseguros.

## 7. Construir y levantar el stack

Desde la raíz del repo:

```bash
cd /opt/tfg
docker compose up -d --build
```

Comprobar estado:

```bash
docker compose ps
```

Ver logs si algo falla:

```bash
docker compose logs -f
```

Ver logs de un servicio concreto:

```bash
docker compose logs -f nginx
docker compose logs -f backend
docker compose logs -f db
```

## 8. Comprobar que el despliegue responde

Desde el propio servidor:

```bash
curl http://localhost/
curl http://localhost/health
curl http://localhost/docs
```

Desde tu navegador:

```text
http://IP_DEL_SERVIDOR/
http://IP_DEL_SERVIDOR/health
http://IP_DEL_SERVIDOR/docs
```

## 9. Comandos útiles de operación

Parar servicios:

```bash
docker compose down
```

Reiniciar servicios:

```bash
docker compose restart
```

Reconstruir y desplegar cambios:

```bash
git pull
docker compose up -d --build
```

Eliminar contenedores y redes del proyecto:

```bash
docker compose down
```

Eliminar también volúmenes de PostgreSQL:

```bash
docker compose down -v
```

Atención:

- `docker compose down -v` borra la base de datos persistida.

## 10. Actualización típica del proyecto

```bash
cd /opt/tfg
git pull
docker compose up -d --build
docker compose ps
```

## 11. Si el repo no está en GitHub y quieres subirlo manualmente

Desde tu equipo local, en la carpeta del proyecto:

```bash
scp -r ./ usuario@IP_DEL_SERVIDOR:/opt/tfg
```

Luego en el servidor:

```bash
cd /opt/tfg
docker compose up -d --build
```

## 12. Recomendaciones mínimas para no dejarlo frágil

- Cambia `DB_PASSWORD` y `SECRET_KEY` por valores reales y largos.
- No abras `5432` en el firewall salvo necesidad explícita.
- Usa un usuario no root con `sudo`.
- Haz copia del `.env` y de los datos si el proyecto es importante.
- Cuando toque sacar esto a producción real, el siguiente paso es meter HTTPS con un proxy inverso y certificado.

## 13. Resumen corto de comandos

Instalación base:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg git ufw openssl
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

Despliegue:

```bash
cd /opt
git clone URL_DEL_REPO tfg
cd /opt/tfg
cp .env.example .env
nano .env
docker compose up -d --build
docker compose ps
```