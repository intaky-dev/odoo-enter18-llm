# 🚀 Guía Rápida de Instalación - LLM MCP Server

## Opción 1: Instalación Manual (Recomendada)

### 1. Levantar Odoo

```bash
cd /home/intaky/Desktop/Dev/odoo-enter18-llm
docker-compose up -d
```

### 2. Acceder a la interfaz web

1. Abre tu navegador en: **http://localhost:8069**
2. Inicia sesión con:
   - **Usuario:** admin
   - **Contraseña:** admin

### 3. Activar Modo Desarrollador

1. Ve a: **Settings** (Configuración)
2. Scroll hasta el final de la página
3. Click en **"Activate the developer mode"**

### 4. Actualizar lista de aplicaciones

1. Ve a: **Apps** (Aplicaciones)
2. En el menú superior, click en el menú de 3 puntos (⋮)
3. Selecciona **"Update Apps List"**
4. Confirma la actualización

### 5. Instalar módulos en este orden

**Importante:** Instala en este orden exacto:

#### a) web_json_editor
1. En Apps, busca: `web_json_editor`
2. Click en **Install**

#### b) LLM Integration Base
1. Busca: `llm` o `LLM Integration Base`
2. Click en **Install**
3. Espera a que complete (puede tardar unos minutos)

#### c) LLM Tool
1. Busca: `llm_tool`
2. Click en **Install**

#### d) LLM MCP Server
1. Busca: `llm_mcp_server` o `LLM MCP Server`
2. Click en **Install**
3. ¡Este es el módulo principal!

### 6. Generar API Key

1. Ve a: **Settings → Users & Companies → Users**
2. Selecciona tu usuario (**admin**)
3. Ve a la pestaña **"API Keys"**
4. Click en **"New"** o **"Generate"**
5. **¡COPIA LA API KEY INMEDIATAMENTE!** (solo se muestra una vez)

### 7. Configurar Claude Code

Edita: `~/.config/claude/claude_desktop_config.json`

Reemplaza `YOUR_ODOO_API_KEY_HERE` con tu API key:

```json
{
  "mcpServers": {
    "odoo": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:8069/mcp/v1",
        "tu_api_key_aqui"
      ]
    }
  }
}
```

### 8. Reiniciar Claude Code

Cierra y vuelve a abrir Claude Code.

### 9. Verificar

En Claude Code, pregunta:
```
"¿Qué herramientas MCP tienes disponibles?"
```

Deberías ver las herramientas de Odoo listadas.

---

## Opción 2: Script Automático (Experimental)

Si prefieres intentar con el script automático:

```bash
cd /home/intaky/Desktop/Dev/odoo-enter18-llm
python3 install_llm_modules.py
```

**Nota:** El script puede fallar debido a limitaciones de la API XML-RPC.
En ese caso, usa la Opción 1 (Manual).

---

## 🆘 Solución de Problemas

### Los módulos no aparecen en Apps

1. Verifica que el modo desarrollador esté activo
2. Actualiza la lista de aplicaciones (Update Apps List)
3. Elimina el filtro "Apps" de la barra de búsqueda
4. Intenta buscar por nombre técnico: `llm`, `llm_mcp_server`, etc.

### No puedo generar API Key

1. Asegúrate de tener el módulo **web_settings_dashboard** instalado
2. Verifica que tu usuario sea administrador
3. Intenta desde: Settings → Technical → Security → Users

### El servidor MCP no conecta

1. Verifica que el módulo `llm_mcp_server` esté instalado
2. Comprueba la URL: http://localhost:8069/mcp/v1
3. Revisa que la API key sea correcta
4. Mira los logs: `docker logs odoo-enterprise`

### Error 404 en /mcp/v1

El módulo `llm_mcp_server` no está instalado correctamente. Reinstálalo.

---

## 📋 Verificación Post-Instalación

Puedes verificar que todo funcione ejecutando:

```bash
curl -H "Authorization: Bearer TU_API_KEY" http://localhost:8069/mcp/v1/tools/list
```

Debería retornar un JSON con la lista de herramientas disponibles.

---

## 🔗 Enlaces Útiles

- [Repositorio Apexive LLM](https://github.com/apexive/odoo-llm)
- [Odoo Apps - LLM MCP Server](https://apps.odoo.com/apps/modules/18.0/llm_mcp_server)
- [Model Context Protocol Docs](https://modelcontextprotocol.io/)

---

**¿Problemas?** Lee el archivo `LLM_INSTALLATION.md` para más detalles.
