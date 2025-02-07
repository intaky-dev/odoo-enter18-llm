FROM ubuntu:22.04

# Configuración del entorno
ENV ODOO_VERSION=18.0
ENV ODOO_PACKAGE=odoo_18.0+e.latest_all.deb
ENV DEBIAN_FRONTEND=noninteractive

# Actualizar repositorios e instalar dependencias de Ubuntu
RUN apt-get update && apt-get install -y apt-utils \
    python3 python3-pip python3-dev python3-venv \
    libxml2-dev libxslt1-dev libevent-dev \
    libsasl2-dev libldap2-dev libpq-dev \
    libjpeg-dev zlib1g-dev libfreetype6-dev \
    build-essential wget curl sudo \
    postgresql-client nano fish mc \
    fonts-inconsolata fonts-font-awesome fonts-roboto-unhinted gsfonts \
    python3-wheel python3-setuptools cython3 \
    locales-all \
    python3-asn1crypto python3-babel python3-cbor2 python3-chardet \
    python3-cryptography python3-dateutil python3-decorator \
    python3-docutils python3-geoip2 python3-gevent python3-greenlet \
    python3-idna python3-jinja2 python3-libsass python3-lxml \
    python3-markupsafe python3-num2words python3-ofxparse \
    python3-openpyxl python3-openssl python3-passlib python3-pil \
    python3-polib python3-psutil python3-psycopg2 python3-pypdf2 \
    python3-qrcode python3-reportlab python3-requests python3-rjsmin \
    python3-serial python3-stdnum python3-tz python3-urllib3 \
    python3-usb python3-vobject python3-werkzeug python3-xlrd \
    python3-xlsxwriter python3-xlwt python3-zeep python3-freezegun \
    python3-renderpm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar locales y configurar es_AR.UTF-8
RUN apt-get install -y locales && \
    locale-gen es_AR.UTF-8 && \
    update-locale LANG=es_AR.UTF-8

# Crear usuario para Odoo
RUN useradd -m -d /opt/odoo -U -r -s /bin/bash odoo

# Copiar el paquete .deb al contenedor
COPY $ODOO_PACKAGE /tmp/

# Instalar el paquete .deb asegurando la instalación de dependencias
RUN dpkg -i /tmp/$ODOO_PACKAGE || apt-get install -fy

# Copiar los requisitos de Python al contenedor
COPY requirements.txt /tmp/

# Instalar dependencias de Python
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Descargar wait-for-it (script para esperar servicios)
RUN wget -O /usr/local/bin/wait-for-it https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it

# Configurar permisos
RUN chown -R odoo:odoo /opt/odoo

# Definir el usuario de ejecución
USER odoo

# Exponer los puertos de Odoo
EXPOSE 8069 8071

# Comando de arranque para esperar que PostgreSQL esté listo antes de iniciar Odoo
CMD ["wait-for-it", "db:5432", "--", "/usr/bin/odoo", "-i", "base", "--database=odoo"]
