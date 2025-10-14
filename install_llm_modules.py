#!/usr/bin/env python3
"""
Automated installation and verification script for Odoo LLM MCP Server modules
Based on the installation pattern from modulo_rg5329
"""

import xmlrpc.client
import time
import sys

# Odoo connection parameters
url = 'http://localhost:8069'
db = 'odoo'
username = 'admin'
password = 'admin'

# Modules to install in order (dependencies first)
MODULES_TO_INSTALL = [
    'web_json_editor',  # Dependency
    'llm',              # Base LLM integration
    'llm_tool',         # LLM tools
    'llm_mcp_server',   # MCP server
]

def connect_to_odoo():
    """Establish connection to Odoo instance"""
    print("\n" + "="*80)
    print("🔌 CONNECTING TO ODOO")
    print("="*80)

    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})

        if uid:
            models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
            print(f"✅ Connected to Odoo as user ID: {uid}")
            return uid, models
        else:
            print("❌ Authentication failed")
            print("💡 Verify your credentials in the script:")
            print(f"   - URL: {url}")
            print(f"   - Database: {db}")
            print(f"   - Username: {username}")
            return None, None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        print("💡 Make sure Odoo is running on http://localhost:8069")
        return None, None

def check_module_state(models, uid, password, module_name):
    """Check if a module is installed"""
    try:
        modules = models.execute_kw(db, uid, password, 'ir.module.module', 'search_read', [
            [('name', '=', module_name)]
        ], {'fields': ['name', 'state'], 'limit': 1})

        if modules:
            return modules[0]['state']
        return None
    except Exception as e:
        print(f"⚠️  Error checking module {module_name}: {e}")
        return None

def install_module(models, uid, password, module_name):
    """Install a specific module"""
    print(f"\n📦 Installing module: {module_name}")

    state = check_module_state(models, uid, password, module_name)

    if state == 'installed':
        print(f"✅ Module {module_name} is already installed")
        return True

    if state == 'uninstalled' or state == 'to install':
        try:
            # Get module ID
            module_ids = models.execute_kw(db, uid, password, 'ir.module.module', 'search', [
                [('name', '=', module_name)]
            ])

            if not module_ids:
                print(f"❌ Module {module_name} not found in addons path")
                print(f"💡 Make sure the module is in: /opt/odoo/custom-addons/")
                return False

            # Install module
            models.execute_kw(db, uid, password, 'ir.module.module', 'button_immediate_install', [module_ids])

            print(f"⏳ Installing {module_name}... (this may take a moment)")
            time.sleep(3)

            # Verify installation
            state = check_module_state(models, uid, password, module_name)
            if state == 'installed':
                print(f"✅ Module {module_name} installed successfully")
                return True
            else:
                print(f"⚠️  Module {module_name} state: {state}")
                return False

        except Exception as e:
            print(f"❌ Error installing {module_name}: {e}")
            return False
    else:
        print(f"⚠️  Module {module_name} is in unexpected state: {state}")
        return False

def update_module_list(models, uid, password):
    """Update the module list in Odoo"""
    print("\n🔄 Updating module list...")
    try:
        # In Odoo 18, update_list() doesn't take a list argument
        models.execute_kw(db, uid, password, 'ir.module.module', 'update_list', [])
        print("✅ Module list updated")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"❌ Error updating module list: {e}")
        return False

def verify_mcp_server(models, uid, password):
    """Verify MCP server functionality"""
    print("\n" + "="*80)
    print("🔍 VERIFYING MCP SERVER INSTALLATION")
    print("="*80)

    # Check if llm_mcp_server is installed
    state = check_module_state(models, uid, password, 'llm_mcp_server')

    if state == 'installed':
        print("✅ LLM MCP Server module is installed")

        # Check if MCP endpoint is accessible (basic check)
        print("\n📡 MCP Server should be accessible at:")
        print(f"   {url}/mcp/v1")
        print("\n💡 To use with Claude Code, you need to:")
        print("   1. Generate an API key in Odoo (Settings → Users → Your User → API Keys)")
        print("   2. Update claude_desktop_config.json with your API key")
        print("   3. Restart Claude Code")

        return True
    else:
        print(f"❌ LLM MCP Server not properly installed (state: {state})")
        return False

def main():
    """Main installation workflow"""
    print("\n" + "="*80)
    print("🚀 ODOO LLM MCP SERVER - AUTOMATED INSTALLATION")
    print("="*80)
    print("\nThis script will install the following modules:")
    for module in MODULES_TO_INSTALL:
        print(f"  • {module}")
    print("\n" + "="*80)

    # Connect to Odoo
    uid, models = connect_to_odoo()
    if not uid or not models:
        print("\n❌ Installation aborted: Could not connect to Odoo")
        return False

    # Update module list
    if not update_module_list(models, uid, password):
        print("\n⚠️  Warning: Could not update module list, continuing anyway...")

    # Install modules in order
    print("\n" + "="*80)
    print("📦 INSTALLING MODULES")
    print("="*80)

    all_success = True
    for module in MODULES_TO_INSTALL:
        success = install_module(models, uid, password, module)
        if not success:
            print(f"\n❌ Failed to install {module}")
            all_success = False
            # Continue with other modules even if one fails

    if not all_success:
        print("\n⚠️  Some modules failed to install")
        print("💡 Check the Odoo logs for more details:")
        print("   docker logs -f odoo-enterprise")
        return False

    # Verify MCP server
    if not verify_mcp_server(models, uid, password):
        return False

    # Success summary
    print("\n" + "="*80)
    print("🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\n✅ All modules installed:")
    for module in MODULES_TO_INSTALL:
        print(f"  • {module}")

    print("\n📋 NEXT STEPS:")
    print("1. Generate API Key in Odoo:")
    print("   Settings → Users & Companies → Users → admin → API Keys")
    print("   Click 'New' and copy the generated key")
    print("\n2. Update Claude Code configuration:")
    print("   File: ~/.config/claude/claude_desktop_config.json")
    print(f'   Replace "YOUR_ODOO_API_KEY_HERE" with your actual API key')
    print("\n3. Restart Claude Code to load the new MCP server")
    print("\n4. Test the connection by asking Claude to interact with Odoo")
    print("\n" + "="*80)

    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
