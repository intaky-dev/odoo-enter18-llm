# 🎯 Instalación Manual - Paso a Paso

La instalación automática tiene limitaciones en Odoo 18 debido a cambios en la API XML-RPC.
Esta guía te llevará paso a paso por la instalación manual (5-10 minutos).

## ✅ Pre-requisitos

El script `install.sh` ya verificó que:
- ✅ Odoo está corriendo
- ✅ Los módulos están en el contenedor
- ✅ La base de datos existe

## 📝 Pasos para Instalar

### 1. Abrir Odoo

Abre tu navegador en: **http://localhost:8069**

### 2. Iniciar Sesión

```
Usuario: admin
Contraseña: admin
```

### 3. Activar Modo Desarrollador

1. Click en **Settings** (⚙️ Configuración) en el menú superior
2. Scroll hasta el final de la página
3. Click en **"Activate the developer mode"** (Activar modo desarrollador)
   - Si no lo ves, busca en la esquina inferior derecha

### 4. Actualizar Lista de Aplicaciones

1. Click en **Apps** (📦 Aplicaciones) en el menú superior
2. En la barra de búsqueda, **elimina** el filtro "Apps"
3. Click en el menú de 3 puntos verticales (**⋮**) en la esquina superior derecha
4. Selecciona **"Update Apps List"**
5. Click **"Update"** en el diálogo de confirmación
6. Espera unos segundos a que complete

### 5. Instalar Módulos (EN ESTE ORDEN)

#### A) web_json_editor

1. En la barra de búsqueda de Apps, escribe: `json`
2. Deberías ver: **"Web JSON Editor"**
3. Click en **"Install"** (Instalar)
4. Espera a que complete (unos segundos)

#### B) LLM Integration Base

1. En la barra de búsqueda, escribe: `llm` o `LLM Integration`
2. Deberías ver: **"LLM Integration Base"**
3. Click en **"Install"**
4. **IMPORTANTE:** Este puede tardar 30-60 segundos
5. Espera a que la página recargue

#### C) LLM Tool

1. Busca: `llm_tool` o `LLM Tool`
2. Deberías ver: **"LLM Tool"**
3. Click en **"Install"**
4. Espera a que complete

#### D) LLM MCP Server

1. Busca: `llm_mcp_server` o `MCP Server`
2. Deberías ver: **"LLM MCP Server"**
3. Click en **"Install"**
4. **¡Este es el módulo principal!**
5. Espera a que complete

### 6. Verificar Instalación

Después de instalar todos los módulos:

1. Ve a **Apps**
2. Busca `llm`
3. Deberías ver los 4 módulos con estado **"Installed"** (verde)

## 🔑 Generar API Key

### 1. Ir a Usuarios

1. Click en **Settings** (⚙️) → **Users & Companies** → **Users**
2. Click en tu usuario (**admin**)

### 2. Pestaña API Keys

1. Click en la pestaña **"API Keys"** (puede estar en **More** → **API Keys**)
2. Click en **"New"** o **"Generate"**
3. Dale un nombre: `Claude Code MCP`
4. **¡COPIA LA API KEY INMEDIATAMENTE!**
   - Solo se muestra una vez
   - Ejemplo: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

### 3. Guardar en lugar seguro

Guarda la API key en un archivo temporal:

```bash
echo "TU_API_KEY_AQUI" > ~/odoo_api_key.txt
```

## 🔧 Configurar Claude Code

### 1. Editar configuración

```bash
nano ~/.config/claude/claude_desktop_config.json
```

### 2. Buscar la sección "odoo"

Debería verse así:

```json
"odoo": {
  "command": "npx",
  "args": [
    "-y",
    "mcp-remote",
    "http://localhost:8069/mcp/v1",
    "YOUR_ODOO_API_KEY_HERE"
  ]
}
```

### 3. Reemplazar la API key

Reemplaza `YOUR_ODOO_API_KEY_HERE` con tu API key real:

```json
"odoo": {
  "command": "npx",
  "args": [
    "-y",
    "mcp-remote",
    "http://localhost:8069/mcp/v1",
    "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
  ]
}
```

### 4. Guardar y cerrar

- En nano: `Ctrl+X`, luego `Y`, luego `Enter`
- En vim: `Esc`, luego `:wq`, luego `Enter`

## 🚀 Reiniciar Claude Code

Cierra completamente Claude Code y vuelve a abrirlo.

## ✅ Verificar

### Opción 1: Desde Claude Code

Pregunta a Claude:

```
"¿Qué herramientas MCP tienes disponibles para Odoo?"
```

Deberías ver las herramientas listadas.

### Opción 2: Desde la Terminal

```bash
curl -H "Authorization: Bearer TU_API_KEY" \
  http://localhost:8069/mcp/v1/tools/list
```

Debería retornar un JSON con las herramientas disponibles.

## 🎉 ¡Listo!

Ahora puedes usar Claude Code para interactuar con tu instancia de Odoo.

### Ejemplos de lo que puedes hacer:

- "Lista todos los clientes en Odoo"
- "Crea una orden de venta para el cliente X"
- "Busca productos con precio mayor a $1000"
- "Muéstrame las facturas del último mes"

## 🆘 Problemas?

### No veo los módulos después del Update Apps List

1. Asegúrate de haber eliminado el filtro "Apps" de la búsqueda
2. Busca por nombre técnico: `llm`, `llm_mcp_server`, etc.
3. Verifica que el modo desarrollador esté activo

### No puedo generar API Key

1. Verifica que estés logueado como **admin**
2. Intenta desde: Settings → Technical → Security → Users → admin

### El MCP no conecta

1. Verifica que `llm_mcp_server` esté instalado (verde en Apps)
2. Revisa los logs: `docker logs odoo-enterprise`
3. Prueba el endpoint manualmente con curl

---

**Tiempo estimado:** 5-10 minutos

**¿Necesitas ayuda?** Lee el README.md o LLM_INSTALLATION.md
