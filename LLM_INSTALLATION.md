# 🤖 Instalación de Odoo LLM MCP Server

Esta es una copia de `odoo-enter18` con los módulos LLM de Apexive Solutions preinstalados.

## 📦 Módulos Incluidos

Los siguientes módulos han sido copiados desde [apexive/odoo-llm](https://github.com/apexive/odoo-llm):

- **llm** - Base de integración LLM
- **llm_tool** - Herramientas LLM
- **llm_mcp_server** - Servidor MCP para Claude Code
- **web_json_editor** - Editor JSON (dependencia)

## 🚀 Instalación Rápida

### 1. Levantar Odoo

```bash
cd /home/intaky/Desktop/Dev/odoo-enter18-llm
docker-compose up -d
```

### 2. Esperar a que Odoo esté listo

```bash
# Ver los logs
docker logs -f odoo-enterprise

# Esperar el mensaje: "odoo.modules.loading: Modules loaded."
```

### 3. Ejecutar el script de instalación automática

```bash
python3 install_llm_modules.py
```

El script automáticamente:
- ✅ Se conecta a Odoo
- ✅ Actualiza la lista de módulos
- ✅ Instala las dependencias en orden
- ✅ Verifica la instalación
- ✅ Muestra los siguientes pasos

## 🔑 Configuración de API Key

### Generar API Key en Odoo

1. Accede a Odoo: http://localhost:8069
2. Ve a: **Settings → Users & Companies → Users**
3. Selecciona tu usuario (admin)
4. Ve a la pestaña **"API Keys"**
5. Click en **"New"**
6. Copia la API key generada

### Actualizar Claude Code

La configuración ya está agregada en:
```
~/.config/claude/claude_desktop_config.json
```

Solo necesitas reemplazar `YOUR_ODOO_API_KEY_HERE` con tu API key real:

```json
"odoo": {
  "command": "npx",
  "args": [
    "-y",
    "mcp-remote",
    "http://localhost:8069/mcp/v1",
    "TU_API_KEY_AQUI"
  ]
}
```

### Reiniciar Claude Code

Cierra y vuelve a abrir Claude Code para que cargue la nueva configuración.

## ✅ Verificación

Para verificar que todo está funcionando:

1. En Claude Code, pregunta: "¿Qué herramientas MCP tienes disponibles?"
2. Deberías ver las herramientas de Odoo listadas
3. Prueba con: "Lista los módulos instalados en Odoo"

## 🔧 Instalación Manual (alternativa)

Si prefieres instalar manualmente:

1. Accede a Odoo: http://localhost:8069
2. Ve a **Apps** (Aplicaciones)
3. Elimina el filtro "Apps" de la barra de búsqueda
4. Busca e instala en este orden:
   - `web_json_editor`
   - `llm` (LLM Integration Base)
   - `llm_tool`
   - `llm_mcp_server`

## 📝 Credenciales por Defecto

Según tu `.env`:

- **Database:** odoo
- **User:** odoo
- **Password:** SuperSecret123!
- **Admin Password:** Admin_Passw!

Para iniciar sesión en Odoo:
- **User:** admin
- **Password:** admin (o el que hayas configurado)

## 🆘 Solución de Problemas

### Error: "Module not found"

```bash
# Reiniciar Odoo
docker-compose restart odoo

# Verificar que los módulos estén en el directorio correcto
ls -la addons/ | grep llm
```

### Error de conexión al ejecutar el script

```bash
# Verificar que Odoo esté corriendo
docker ps | grep odoo

# Ver los logs
docker logs odoo-enterprise
```

### Módulos no aparecen en Apps

1. Activa el modo desarrollador: Settings → Activate Developer Mode
2. Ve a Apps → Update Apps List
3. Busca nuevamente los módulos

## 📚 Recursos

- [Repositorio Apexive LLM](https://github.com/apexive/odoo-llm)
- [Documentación MCP](https://modelcontextprotocol.io/)
- [Apps Odoo - LLM MCP Server](https://apps.odoo.com/apps/modules/18.0/llm_mcp_server)

## 🔄 Diferencias con odoo-enter18 Original

Esta instalación es idéntica a `odoo-enter18` excepto por:

1. Módulos LLM en `addons/`:
   - llm
   - llm_tool
   - llm_mcp_server
   - web_json_editor

2. Script de instalación: `install_llm_modules.py`

3. Este archivo de documentación: `LLM_INSTALLATION.md`

---

**Creado:** 2025-10-14
**Basado en:** odoo-enter18 + apexive/odoo-llm
