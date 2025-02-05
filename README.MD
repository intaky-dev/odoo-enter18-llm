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
