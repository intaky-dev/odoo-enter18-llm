# 🏗️ Odoo 18 Enterprise - Dockerized 🚀

Este repositorio contiene la configuración para ejecutar **Odoo 18 Enterprise** en un entorno **Docker** junto con **PostgreSQL** como base de datos.

## 📌 Características
- 🐳 Contenedor de **Odoo 18 Enterprise** basado en Ubuntu 22.04.
- 🛢️ **PostgreSQL 15** como base de datos.
- 🔄 **Auto-reinicio** de los servicios con `restart: always`.
- 🔑 Uso de **variables de entorno** en un archivo `.env` para credenciales seguras.
- 📂 **Persistencia de datos** con volúmenes Docker.
- 🛠️ Soporte para **entorno virtual de Python** (`venv`) para evitar conflictos con permisos.

---

## 🚀 Requisitos previos
Antes de comenzar, asegúrate de tener instalado:
- **Docker** → [Instalar Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** → [Instalar Docker Compose](https://docs.docker.com/compose/install/)

---

## 🔧 Instalación y Configuración

### 📁 1️⃣ Clonar el repositorio
```sh
git clone git@github.com:FW-CORP/odoo-enter18.git
cd odoo-enter18

📥 2️⃣ Descargar el paquete .deb
Como GitHub no permite archivos mayores a 100MB en repositorios, el .deb de Odoo se encuentra en GitHub Releases.
Descárgalo con el siguiente comando:


wget https://github.com/FW-CORP/odoo-enter18/releases/download/v18.0-enterprise/odoo_18.0+e.latest_all.deb -P .
O puedes ir a la página de Releases y descargarlo manualmente: 🔗 Descargar el .deb desde GitHub Releases

⚙️ 3️⃣ Configurar el entorno
Edita el archivo .env para definir las credenciales de PostgreSQL y Odoo:

POSTGRES_DB=odoo
POSTGRES_USER=odoo
POSTGRES_PASSWORD=SuperSecret123!
ODOO_ADMIN_PASSWORD=Glider913!

🏗️ 4️⃣ Construir y levantar los servicios

docker-compose up -d --build
Esto iniciará los contenedores de Odoo y PostgreSQL.
El servicio de Odoo estará disponible en:
🔗 http://localhost:8069

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

RUN python3 -m venv /opt/odoo/venv && \
    source /opt/odoo/venv/bin/activate && \
    pip install --no-cache-dir -r /tmp/requirements.txt

📌 Odoo ahora usa este entorno virtualizado en su arranque:
CMD ["/opt/odoo/venv/bin/python", "/usr/bin/odoo"]

⚠️ 2. Error invoke-rc.d: could not determine current runlevel
💡 Causa: Odoo intenta ejecutarse durante la instalación del .deb, pero en Docker no hay un sistema init como systemd.

✅ Solución aplicada en Dockerfile:

RUN dpkg --configure -a && update-rc.d -f odoo remove


🔥 Comandos Útiles
📌 Ver logs de Odoo

docker logs -f odoo-enterprise
📌 Acceder a la base de datos PostgreSQL

docker exec -it odoo-db psql -U odoo -d odoo -h db
📌 Reiniciar Odoo manualmente

docker-compose restart odoo


