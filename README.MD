📌 README

# 🏗️ Odoo 18 Enterprise - Dockerized 🚀

Este repositorio contiene la configuración para ejecutar **Odoo 18 Enterprise** en un entorno **Docker** junto con **PostgreSQL** como base de datos.

---

## 📌 Características
- 🐳 Contenedor de **Odoo 18 Enterprise** basado en Ubuntu 22.04.
- 🛢️ **PostgreSQL 15** como base de datos.
- 🔄 **Auto-reinicio** de los servicios con `restart: always`.
- 🔑 Uso de **variables de entorno** en un archivo `.env` para credenciales seguras.
- 📂 **Persistencia de datos** con volúmenes Docker.
- 🛠️ Soporte para **entorno virtual de Python (`venv`)** para evitar conflictos con permisos.

---

## 🛠️ Importante: ¿Usar `build` o `pull` de Docker Hub? 🤔

Este repositorio soporta **dos formas** de obtener la imagen de Odoo 18 Enterprise:

### ✅ **1️⃣ Método recomendado: Usar la imagen desde Docker Hub**
Si **no quieres construir la imagen manualmente**, simplemente **pullea la imagen preconstruida** desde [Docker Hub](https://hub.docker.com/r/klap50/odoo18-enterprise):

1️⃣ **Edita el `docker-compose.yml`** y usa la imagen de Docker Hub:
```yaml
services:
  odoo:
    image: klap50/odoo18-enterprise:latest
    container_name: odoo-enterprise
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
2️⃣ Levanta el contenedor con:


docker-compose up -d
✅ Si la imagen no está en local, se descargará automáticamente.
✅ Siempre usa docker-compose pull para obtener la versión más reciente.

🔨 2️⃣ Alternativa: Construir la imagen localmente
Si quieres modificar la imagen o hacer pruebas, puedes construirla manualmente:

1️⃣ Edita docker-compose.yml y usa build: en vez de image::

yaml

services:
  odoo:
    build: .
    container_name: odoo-enterprise
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
2️⃣ Construye la imagen y levanta los contenedores con:


docker-compose up -d --build
✅ Este método es útil si has cambiado el Dockerfile y necesitas recompilar la imagen.

🚀 Requisitos previos
Antes de comenzar, asegúrate de tener instalado:

Docker → Instalar Docker
Docker Compose → Instalar Docker Compose
🔧 Instalación y Configuración
📁 1️⃣ Clonar el repositorio

git clone git@github.com:FW-CORP/odoo-enter18.git
cd odoo-enter18
📥 2️⃣ Descargar el paquete .deb
Como GitHub no permite archivos mayores a 100MB en repositorios, el .deb de Odoo se encuentra en GitHub Releases.

Descárgalo con el siguiente comando:


wget https://github.com/FW-CORP/odoo-enter18/releases/download/v18.0-enterprise/odoo_18.0+e.latest_all.deb -P .
O descárgalo manualmente desde:
🔗 Descargar el .deb desde GitHub Releases

⚙️ 3️⃣ Configurar el entorno
Edita el archivo .env para definir las credenciales de PostgreSQL y Odoo:

ini

POSTGRES_DB=odoo
POSTGRES_USER=odoo
POSTGRES_PASSWORD=SuperSecret123!
ODOO_ADMIN_PASSWORD=Glider913!
🏗️ 4️⃣ Construir y levantar los servicios

docker-compose up -d --build
✅ Esto iniciará los contenedores de Odoo y PostgreSQL.
🔗 Odoo estará disponible en: http://localhost:8069

📌 Estructura del Proyecto

├── .env                 # Variables de entorno para PostgreSQL y Odoo
├── .gitignore           # Archivos ignorados por Git
├── docker-compose.yml   # Configuración de servicios en Docker
├── Dockerfile           # Configuración del contenedor de Odoo
├── requirements.txt     # Dependencias de Python necesarias para Odoo
├── README.md            # Documentación del proyecto
└── odoo_18.0+e.latest_all.deb  # (Descargar desde Releases)
🛠️ Solución de Problemas
⚠️ 1. Problema con permisos de pip install
💡 Causa: Se está ejecutando pip install como root, lo cual puede generar problemas de permisos.

✅ Solución recomendada: Se instaló un entorno virtual en el Dockerfile para evitar conflictos:

dockerfile

RUN python3 -m venv /opt/odoo/venv && \
    source /opt/odoo/venv/bin/activate && \
    pip install --no-cache-dir -r /tmp/requirements.txt
📌 Odoo ahora usa este entorno virtualizado en su arranque:

dockerfile

CMD ["/opt/odoo/venv/bin/python", "/usr/bin/odoo"]
⚠️ 2. Error invoke-rc.d: could not determine current runlevel
💡 Causa: Odoo intenta ejecutarse durante la instalación del .deb, pero en Docker no hay un sistema init como systemd.

✅ Solución aplicada en Dockerfile:

dockerfile

RUN dpkg --configure -a && update-rc.d -f odoo remove
🔥 Comandos Útiles
📌 Ver logs de Odoo

docker logs -f odoo-enterprise
📌 Acceder a la base de datos PostgreSQL

docker exec -it odoo-db psql -U odoo -d odoo -h db
📌 Reiniciar Odoo manualmente

docker-compose restart odoo
🎯 Próximos Pasos
✅ Verificar que Odoo funcione correctamente con la localización en español (l10n_es).
✅ Probar instalación de módulos críticos (ventas, facturación, contabilidad).
✅ Configurar HTTPS con Traefik o Nginx (opcional).
