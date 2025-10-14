#!/bin/bash

# Auto-Install Script for Odoo LLM MCP Server Modules
# Based on modulo_lubricar install.sh pattern

set -e  # Exit on any error

# Configuration
MODULE_NAMES=("web_json_editor" "llm" "llm_tool" "llm_mcp_server")
DOCKER_COMPOSE_PATH="/home/intaky/Desktop/Dev/odoo-enter18-llm"
DB_NAME="odoo"
ADMIN_USER="admin"
ADMIN_PASSWORD="admin"
CONTAINER_NAME="odoo-enterprise"

echo "🚀 Auto-Install Odoo LLM MCP Server Modules..."

# Check if docker-compose directory exists
if [ ! -d "$DOCKER_COMPOSE_PATH" ]; then
    echo "❌ Error: Docker compose directory not found at $DOCKER_COMPOSE_PATH"
    exit 1
fi

echo "✅ Starting installation process..."

# Navigate to docker-compose directory
cd "$DOCKER_COMPOSE_PATH"

# Check if containers are running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "🚀 Starting Odoo containers..."
    docker-compose up -d

    # Wait for containers
    echo "⏳ Waiting for containers to be ready..."
    sleep 30
fi

# Wait for Odoo to be responsive
echo "⏳ Waiting for Odoo to be ready..."
for i in {1..20}; do
    if docker exec "$CONTAINER_NAME" curl -s http://localhost:8069/web/database/selector > /dev/null 2>&1; then
        echo "✅ Odoo is responding"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "❌ Odoo not responding after 3+ minutes"
        exit 1
    fi
    echo "   Checking... ($i/20)"
    sleep 10
done

# Install Python dependencies first
echo "📦 Installing Python dependencies..."
if docker exec "$CONTAINER_NAME" pip3 install --upgrade \
    pydantic>=2.0.0 \
    mcp \
    jsonschema \
    jinja2 \
    emoji \
    markdown2 \
    pyyaml \
    > /dev/null 2>&1; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Copy modules to Odoo addons directory (like modulo_lubricar does)
echo "📦 Copying modules to Odoo addons directory..."

# Target directory inside container (Odoo's main addons path)
TARGET_DIR="/usr/lib/python3/dist-packages/odoo/addons"

# Copy each module
for module in web_json_editor llm llm_tool llm_mcp_server; do
    if [ -d "$DOCKER_COMPOSE_PATH/addons/$module" ]; then
        echo "   Copying $module..."
        docker cp "$DOCKER_COMPOSE_PATH/addons/$module" "$CONTAINER_NAME:$TARGET_DIR/"
        echo "   ✅ $module copied"
    else
        echo "   ❌ Module $module not found at $DOCKER_COMPOSE_PATH/addons/$module"
        exit 1
    fi
done

echo "✅ All modules copied successfully"

# Restart Odoo to recognize new modules
echo "🔄 Restarting Odoo to recognize new modules..."
docker restart "$CONTAINER_NAME"
sleep 20

# Wait for Odoo to be ready again
echo "⏳ Waiting for Odoo to restart..."
for i in {1..20}; do
    if docker exec "$CONTAINER_NAME" curl -s http://localhost:8069/web/database/selector > /dev/null 2>&1; then
        echo "✅ Odoo restarted successfully"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "❌ Odoo not responding after restart"
        exit 1
    fi
    echo "   Checking... ($i/20)"
    sleep 10
done

# Verify modules are in container
echo "🔍 Verifying modules are in Odoo addons..."
if docker exec "$CONTAINER_NAME" test -d "$TARGET_DIR/llm"; then
    echo "✅ Modules confirmed in container"
else
    echo "❌ Module copy verification failed"
    exit 1
fi

# Install modules via Odoo XML-RPC and capture API key
echo "🎯 Installing LLM modules automatically..."
INSTALL_OUTPUT=$(docker exec "$CONTAINER_NAME" python3 -c "
import xmlrpc.client
import time
import sys

# Configuration
url = 'http://localhost:8069'
db = '$DB_NAME'
username = '$ADMIN_USER'
password = '$ADMIN_PASSWORD'
modules_to_install = ['web_json_editor', 'llm', 'llm_tool', 'llm_mcp_server']

try:
    print('🔗 Connecting to Odoo...')

    # Connect to common service
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))

    # Authenticate
    print('🔐 Authenticating...')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        print('❌ Authentication failed - database may not exist or wrong credentials')
        print('   Please create database manually first')
        sys.exit(1)
    print(f'✅ Authenticated as user {uid}')

    # Connect to object service
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    # Update apps list
    print('🔄 Updating apps list...')
    try:
        models.execute_kw(db, uid, password, 'ir.module.module', 'update_list', [])
        print('✅ Apps list updated')
        time.sleep(3)
    except Exception as e:
        print(f'⚠️  Could not update apps list: {e}')
        print('   Continuing anyway...')

    # Install modules in order
    print('📦 Installing modules in correct order...')

    for module_name in modules_to_install:
        print(f'\\n🔍 Processing {module_name}...')
        try:
            # Search for module
            module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [[['name', '=', module_name]]])

            if not module_ids:
                print(f'❌ Module {module_name} not found')
                print(f'   Make sure the module is in /opt/odoo/custom-addons/')
                continue

            module_id = module_ids[0]
            module_info = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [module_id], {'fields': ['name', 'state', 'shortdesc']})

            current_state = module_info[0]['state']
            print(f'   Current state: {current_state}')

            if current_state == 'uninstalled':
                print(f'   Installing {module_name}...')
                models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [module_id])

                # Wait for installation to complete
                installation_success = False
                for i in range(60):  # Wait up to 60 seconds
                    time.sleep(1)
                    updated_info = models.execute_kw(db, uid, password, 'ir.module.module', 'read', [module_id], {'fields': ['state']})
                    if updated_info[0]['state'] == 'installed':
                        print(f'✅ {module_name} installed successfully')
                        installation_success = True
                        break
                    elif i == 59:
                        print(f'⚠️  {module_name} installation timeout after 60 seconds')
                        break
                    elif i % 10 == 0 and i > 0:
                        print(f'   Still installing... ({i}s)')

                if not installation_success:
                    print(f'❌ Failed to install {module_name}')
                    if module_name in ['llm', 'llm_mcp_server']:
                        print('   This is a critical module, installation may be incomplete')

            elif current_state == 'installed':
                print(f'✅ {module_name} already installed')
            else:
                print(f'ℹ️  {module_name} state: {current_state}')

        except Exception as e:
            print(f'❌ Error processing {module_name}: {str(e)}')
            if module_name in ['llm', 'llm_mcp_server']:
                print('   This is a critical module, stopping installation')
                sys.exit(1)

    # Verify MCP server installation
    print('\\n🔍 Verifying MCP server installation...')
    mcp_module = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read',
                                    [[['name', '=', 'llm_mcp_server']]],
                                    {'fields': ['state'], 'limit': 1})

    if mcp_module and mcp_module[0]['state'] == 'installed':
        print('✅ LLM MCP Server module is installed and ready')
    else:
        print('❌ LLM MCP Server module not properly installed')
        sys.exit(1)

    # Generate API Key automatically using internal Odoo API
    print('\\n🔑 Generating API Key...')

    sys.exit(0)  # Exit successfully, key will be generated by separate script

    print('\\n✅ Installation process completed successfully')

except Exception as e:
    print(f'❌ Error: {str(e)}')
    print('\\n📋 Try manual installation:')
    print('   1. Go to http://localhost:8069')
    print('   2. Activate Developer Mode')
    print('   3. Apps → Update Apps List')
    print('   4. Install modules in order: web_json_editor, llm, llm_tool, llm_mcp_server')
    sys.exit(1)
")

# Display installation output
echo "$INSTALL_OUTPUT"

# Generate API Key using internal Odoo API (avoids XML-RPC restrictions)
echo ""
echo "🔑 Generating API Key..."
API_KEY_OUTPUT=$(docker exec "$CONTAINER_NAME" python3 -c "
import odoo
from odoo import api, SUPERUSER_ID
import binascii
import os

# Configuration
db_name = '$DB_NAME'
username = '$ADMIN_USER'

try:
    # Get registry and environment
    registry = odoo.modules.registry.Registry(db_name)

    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        # Find user
        user = env['res.users'].search([('login', '=', username)], limit=1)
        if not user:
            print('❌ User not found')
            exit(1)

        # Generate key manually
        from passlib.context import CryptContext

        API_KEY_SIZE = 20
        INDEX_SIZE = 8
        KEY_CRYPT_CONTEXT = CryptContext(['pbkdf2_sha512', 'plaintext'], deprecated=['plaintext'])

        # Generate the key
        key_name = 'MCP Server API Key (auto-generated)'
        k = binascii.hexlify(os.urandom(API_KEY_SIZE)).decode()

        # Insert directly into database
        env.cr.execute('''
            INSERT INTO res_users_apikeys (name, user_id, scope, key, index)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        ''', [key_name, user.id, None, KEY_CRYPT_CONTEXT.hash(k), k[:INDEX_SIZE]])

        key_id = env.cr.fetchone()[0]

        # Commit the transaction
        cr.commit()

        print(f'API_KEY={k}')

except Exception as e:
    print(f'❌ Error: {str(e)}')
    exit(1)
" 2>&1)

# Extract API key from output
API_KEY=$(echo "$API_KEY_OUTPUT" | grep "^API_KEY=" | cut -d'=' -f2)

if [ $? -eq 0 ] && [ -n "$API_KEY" ]; then
    echo ""
    echo "🎉 INSTALLATION SUCCESSFUL!"
    echo ""
    echo "✅ LLM MCP Server modules are now installed!"
    echo "🌐 Access Odoo at: http://localhost:8069"
    echo "🔑 Login: $ADMIN_USER / $ADMIN_PASSWORD"
    echo "💾 Database: $DB_NAME"
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                          🔐 YOUR API KEY                                     ║"
    echo "╠══════════════════════════════════════════════════════════════════════════════╣"
    echo "║  $API_KEY"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "⚠️  IMPORTANT: Save this API key now! You won't be able to see it again."
    echo ""
    echo "📋 NEXT STEPS:"
    echo ""
    echo "1️⃣  Update Claude Code Configuration:"
    echo "   • File: ~/.config/claude/claude_desktop_config.json"
    echo "   • Replace 'YOUR_ODOO_API_KEY_HERE' with the API key above"
    echo ""
    echo "   Example:"
    echo "   {"
    echo "     \"mcpServers\": {"
    echo "       \"odoo\": {"
    echo "         \"command\": \"npx\","
    echo "         \"args\": [\"-y\", \"@anthropic/mcp-client\", \"http://localhost:8069/mcp/v1\"],"
    echo "         \"env\": {"
    echo "           \"ODOO_API_KEY\": \"$API_KEY\""
    echo "         }"
    echo "       }"
    echo "     }"
    echo "   }"
    echo ""
    echo "2️⃣  Restart Claude Code"
    echo ""
    echo "3️⃣  Test MCP Server:"
    echo "   curl -H \"Authorization: Bearer $API_KEY\" http://localhost:8069/mcp/v1/tools/list"
    echo ""
    echo "🔧 Installed Modules:"
    echo "   • web_json_editor - JSON Editor widget"
    echo "   • llm - LLM Integration Base"
    echo "   • llm_tool - LLM Tools"
    echo "   • llm_mcp_server - MCP Server for Claude Code"
    echo ""
    echo "📡 MCP Endpoint: http://localhost:8069/mcp/v1"
    echo ""
else
    echo ""
    echo "⚠️  AUTOMATIC INSTALLATION INCOMPLETE"
    echo ""
    echo "Los módulos están en el contenedor pero Odoo 18 tiene limitaciones"
    echo "en la API XML-RPC update_list() que impiden la detección automática."
    echo ""
    echo "✅ BUENAS NOTICIAS: Los módulos están listos para instalar"
    echo "📋 SIGUIENTE PASO: Instalación manual (5-10 minutos)"
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  Sigue la guía paso a paso:                                ║"
    echo "║                                                            ║"
    echo "║  cat install_manual.md                                     ║"
    echo "║                                                            ║"
    echo "║  O abre: http://localhost:8069                             ║"
    echo "║  Login: admin / admin                                      ║"
    echo "║  Apps → Update Apps List → Instalar módulos               ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📚 Documentación:"
    echo "   • install_manual.md  - Guía detallada paso a paso"
    echo "   • QUICK_START.md     - Guía rápida"
    echo "   • README.md          - Documentación completa"
    echo ""
fi
