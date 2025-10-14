# 🤖 Odoo 18 Enterprise + LLM MCP Server

Sistema completo de Odoo 18 Enterprise con módulos LLM integrados para Claude Code vía Model Context Protocol (MCP).

## ✨ Características

- ✅ **Instalación automática completa** - Un solo comando instala todo
- ✅ **Generación automática de API Key** - No necesitas crearla manualmente
- ✅ **MCP Server listo para usar** - Integración directa con Claude Code
- ✅ **Docker configurado** - Entorno aislado y reproducible
- ✅ **Módulos LLM pre-incluidos** - De [Apexive Solutions](https://github.com/apexive/odoo-llm)

## 📦 Módulos Incluidos

- **llm** - Base de integración LLM (v18.0.1.4.0)
- **llm_tool** - Herramientas LLM
- **llm_mcp_server** - Servidor MCP para Claude Code
- **web_json_editor** - Editor JSON (dependencia)

## 🚀 Instalación Rápida (Automática)

### Requisitos

- Docker & Docker Compose
- Puerto 8069 disponible
- Git

### Instalación en 3 pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/odoo-enter18-llm.git
cd odoo-enter18-llm

# 2. Ejecutar instalación automática
chmod +x install.sh
./install.sh

# 3. Esperar 5-10 minutos
# El script hará:
# - Levantar contenedores Docker
# - Instalar dependencias Python
# - Copiar módulos LLM
# - Instalar módulos en Odoo
# - Generar API Key automáticamente
```

### Resultado

Al finalizar verás:

```
🎉 INSTALLATION SUCCESSFUL!

╔══════════════════════════════════════════════════════════════════════════════╗
║                          🔐 YOUR API KEY                                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
╚══════════════════════════════════════════════════════════════════════════════╝

⚠️  IMPORTANT: Save this API key now! You won't be able to see it again.
```

**¡Guarda esta API Key!** La necesitarás para configurar Claude Code.

## 🔧 Configuración de Claude Code

### 1. Editar configuración de Claude Code

Abre: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "odoo": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:8069/mcp/v1",
        "TU_API_KEY_AQUI"
      ]
    }
  }
}
```

Reemplaza `TU_API_KEY_AQUI` con la API key que te mostró el script.

### 2. Reiniciar Claude Code

### 3. Verificar conexión

En Claude Code, pregunta:

```
¿Estás conectado a Odoo?
```

O prueba desde terminal:

```bash
curl -H "Authorization: Bearer TU_API_KEY" \
  http://localhost:8069/mcp/v1/tools/list
```

## 📖 Uso con Claude Code

Una vez configurado, puedes pedirle a Claude:

```
"Muéstrame todos los clientes en Odoo"
"Crea un nuevo producto llamado 'Widget Premium'"
"¿Cuántas ventas tenemos este mes?"
"Genera un reporte de inventario"
```

Claude tendrá acceso directo a tu instancia de Odoo vía MCP.

## 🛠️ Instalación Manual (Alternativa)

Si prefieres instalar manualmente:

### 1. Levantar contenedores

```bash
docker-compose up -d
```

### 2. Acceder a Odoo

- URL: http://localhost:8069
- Usuario: `admin`
- Password: `admin`

### 3. Instalar módulos

1. Activar Modo Desarrollador: Settings → Developer Mode
2. Apps → ⋮ → Update Apps List
3. Buscar e instalar en orden:
   - `web_json_editor`
   - `llm`
   - `llm_tool`
   - `llm_mcp_server`

### 4. Generar API Key

Settings → Users & Companies → Users → admin → API Keys → New

Ver **[QUICK_START.md](./QUICK_START.md)** para guía detallada paso a paso.

## 📁 Estructura del Proyecto

```
odoo-enter18-llm/
├── addons/
│   ├── llm/                    # Base LLM integration
│   ├── llm_tool/               # LLM tools
│   ├── llm_mcp_server/         # MCP server
│   ├── web_json_editor/        # JSON editor widget
│   └── ...                     # Otros módulos
├── config/
│   ├── odoo.conf               # Configuración Odoo
│   └── .env                    # Variables de entorno
├── docker-compose.yml          # Docker config
├── install.sh                  # 🌟 Script instalación automática
├── QUICK_START.md              # Guía paso a paso
├── LLM_INSTALLATION.md         # Documentación detallada
└── README.md                   # Este archivo
```

## 🔐 Credenciales por Defecto

**Base de datos:**
- Host: localhost:5432
- Database: odoo
- User: odoo
- Password: SuperSecret123!

**Odoo Web:**
- URL: http://localhost:8069
- Usuario: `admin`
- Password: `admin`

**Admin Password:** Admin_Passw!

## 🆘 Solución de Problemas

### El script install.sh falla

**Síntoma:** Script se detiene o muestra errores

**Solución:**
```bash
# Verificar contenedores corriendo
docker ps

# Ver logs
docker logs odoo-enterprise

# Reintentar
docker-compose restart odoo
./install.sh
```

### Los módulos no aparecen en Apps

**Síntoma:** Después de "Update Apps List", no ves los módulos LLM

**Solución:**
```bash
# Verificar módulos en contenedor
docker exec odoo-enterprise ls -la /usr/lib/python3/dist-packages/odoo/addons/ | grep llm

# Si no están, copiarlos manualmente
docker cp addons/llm odoo-enterprise:/usr/lib/python3/dist-packages/odoo/addons/
docker cp addons/llm_tool odoo-enterprise:/usr/lib/python3/dist-packages/odoo/addons/
docker cp addons/llm_mcp_server odoo-enterprise:/usr/lib/python3/dist-packages/odoo/addons/
docker cp addons/web_json_editor odoo-enterprise:/usr/lib/python3/dist-packages/odoo/addons/

# Reiniciar
docker restart odoo-enterprise
```

### MCP Server no responde (404)

**Síntoma:** `curl` devuelve 404 Not Found

**Causas posibles:**
1. Módulo `llm_mcp_server` no está instalado
2. API Key incorrecta
3. Odoo no está completamente iniciado

**Solución:**
```bash
# Verificar módulo instalado
docker exec odoo-enterprise python3 -c "
import odoo
registry = odoo.modules.registry.Registry('odoo')
with registry.cursor() as cr:
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    module = env['ir.module.module'].search([('name', '=', 'llm_mcp_server')])
    print(f'Estado: {module.state}')
"

# Verificar endpoint
docker logs odoo-enterprise | grep mcp

# Reiniciar Odoo
docker restart odoo-enterprise
```

### Perdí mi API Key

**Síntoma:** Olvidaste guardar la API key generada

**Solución:** Generar una nueva manualmente en Odoo
```
Settings → Users & Companies → Users → admin → API Keys → New
```

O ejecutar este comando:
```bash
docker exec odoo-enterprise python3 -c "
import odoo
from odoo import api, SUPERUSER_ID
import binascii, os
from passlib.context import CryptContext

registry = odoo.modules.registry.Registry('odoo')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    user = env['res.users'].search([('login', '=', 'admin')], limit=1)

    KEY_CRYPT_CONTEXT = CryptContext(['pbkdf2_sha512', 'plaintext'], deprecated=['plaintext'])
    k = binascii.hexlify(os.urandom(20)).decode()

    env.cr.execute('''
        INSERT INTO res_users_apikeys (name, user_id, scope, key, index)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    ''', ['Manual API Key', user.id, None, KEY_CRYPT_CONTEXT.hash(k), k[:8]])

    cr.commit()
    print(f'Nueva API Key: {k}')
"
```

### Puerto 8069 ya está en uso

**Síntoma:** Error al iniciar Docker: "port is already allocated"

**Solución:**
```bash
# Ver qué está usando el puerto
sudo lsof -i :8069

# O cambiar puerto en docker-compose.yml
# Línea: "8069:8069" → "8070:8069"
```

## 📚 Documentación Adicional

- **[QUICK_START.md](./QUICK_START.md)** - Guía paso a paso con capturas
- **[LLM_INSTALLATION.md](./LLM_INSTALLATION.md)** - Documentación técnica completa
- **[install_manual.md](./install_manual.md)** - Guía de instalación manual detallada

### Enlaces Externos

- [Odoo Apps - LLM MCP Server](https://apps.odoo.com/apps/modules/18.0/llm_mcp_server)
- [Repositorio Apexive LLM](https://github.com/apexive/odoo-llm)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Code Docs](https://docs.anthropic.com/claude-code)

## 🔄 Actualización de Módulos

Para actualizar los módulos LLM a versiones más recientes:

```bash
# 1. Descargar nuevas versiones
git clone https://github.com/apexive/odoo-llm.git
cd odoo-llm

# 2. Copiar módulos actualizados
cp -r llm ../odoo-enter18-llm/addons/
cp -r llm_tool ../odoo-enter18-llm/addons/
cp -r llm_mcp_server ../odoo-enter18-llm/addons/

# 3. Reiniciar y actualizar
cd ../odoo-enter18-llm
docker-compose restart odoo
```

En Odoo: Apps → Filtrar por "llm" → Update

## 🤝 Contribuciones

Este proyecto combina:
- **[odoo-enter18](https://github.com/FW-CORP/odoo-enter18)** - Base Odoo 18 Enterprise
- **[odoo-llm](https://github.com/apexive/odoo-llm)** - Módulos LLM de Apexive Solutions

Contribuciones son bienvenidas via Pull Requests.

## 📝 Licencias

- **Odoo 18 Enterprise:** [OEEL-1](https://www.odoo.com/documentation/18.0/legal/licenses.html#odoo-enterprise-edition-license) (Odoo Enterprise Edition License)
- **Módulos LLM:** [LGPL-3.0](https://www.gnu.org/licenses/lgpl-3.0.html)
- **Scripts de instalación:** MIT License

## ⚠️ Advertencias

- Este es un entorno de **desarrollo/testing**
- No usar en producción sin revisar configuración de seguridad
- Las API keys dan acceso completo a Odoo
- Los módulos LLM están en desarrollo activo
- La API MCP está en preview

## 🎯 Casos de Uso

Con esta integración puedes:

- 📊 Generar reportes con lenguaje natural
- 🔍 Buscar y analizar datos de Odoo
- ✏️ Crear y modificar registros
- 🤖 Automatizar tareas repetitivas
- 📈 Analizar tendencias y métricas
- 💬 Interactuar con Odoo conversacionalmente

## 📞 Soporte

Para problemas o preguntas:
1. Revisar sección [Solución de Problemas](#-solución-de-problemas)
2. Consultar documentación en `docs/`
3. Abrir un Issue en GitHub
4. Revisar logs: `docker logs -f odoo-enterprise`

---

**Creado:** 2025-10-14
**Versión Odoo:** 18.0+e (Enterprise)
**Versión Módulos LLM:** 18.0.1.x
**Script de instalación:** v2.0 (con auto-generación de API key)

**Repositorio:** https://github.com/TU_USUARIO/odoo-enter18-llm

---

¡Disfruta de Odoo potenciado con IA! 🚀
