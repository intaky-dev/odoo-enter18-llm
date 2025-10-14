#!/usr/bin/env python3
"""
Odoo 18 Development Agent
========================

An intelligent agent for reviewing and creating Odoo 18 code following best practices.
Supports MVC architecture validation, code generation, and compliance checking.
"""

import os
import re
import json
import ast
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class IssueLevel(Enum):
    ERROR = "error"
    WARNING = "warning" 
    INFO = "info"
    SUGGESTION = "suggestion"

@dataclass
class CodeIssue:
    level: IssueLevel
    message: str
    file_path: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None
    
class OdooAgent:
    """Main agent class for Odoo 18 code analysis and generation"""
    
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.addons_path = self.project_path / "addons"
        self.issues: List[CodeIssue] = []
        
        # Odoo 18 patterns and conventions
        self.odoo_patterns = {
            'model_naming': re.compile(r'^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$'),
            'field_naming': re.compile(r'^[a-z][a-z0-9_]*$'),
            'method_naming': re.compile(r'^[a-z][a-z0-9_]*$'),
            'class_naming': re.compile(r'^[A-Z][a-zA-Z0-9]*$'),
            'file_naming': re.compile(r'^[a-z][a-z0-9_]*\.py$'),
        }
        
        self.required_manifest_keys = [
            'name', 'version', 'depends', 'data', 'installable'
        ]
        
        self.recommended_manifest_keys = [
            'category', 'summary', 'description', 'author', 'license'
        ]

    def analyze_module(self, module_name: str) -> Dict[str, Any]:
        """Comprehensive analysis of an Odoo module"""
        module_path = self.addons_path / module_name
        
        if not module_path.exists():
            return {"error": f"Module {module_name} not found"}
        
        analysis = {
            "module_name": module_name,
            "path": str(module_path),
            "structure": self._analyze_structure(module_path),
            "manifest": self._analyze_manifest(module_path),
            "models": self._analyze_models(module_path),
            "views": self._analyze_views(module_path),
            "controllers": self._analyze_controllers(module_path),
            "security": self._analyze_security(module_path),
            "issues": []
        }
        
        # Add collected issues to analysis
        analysis["issues"] = [asdict(issue) for issue in self.issues]
        self.issues.clear()
        
        return analysis

    def _analyze_structure(self, module_path: Path) -> Dict[str, Any]:
        """Analyze module directory structure"""
        structure = {
            "has_manifest": (module_path / "__manifest__.py").exists(),
            "has_init": (module_path / "__init__.py").exists(),
            "directories": [],
            "python_files": [],
            "xml_files": [],
        }
        
        for item in module_path.iterdir():
            if item.is_dir():
                structure["directories"].append(item.name)
            elif item.suffix == ".py":
                structure["python_files"].append(item.name)
            elif item.suffix == ".xml":
                structure["xml_files"].append(item.name)
        
        # Check required structure
        if not structure["has_manifest"]:
            self.issues.append(CodeIssue(
                level=IssueLevel.ERROR,
                message="Missing __manifest__.py file",
                file_path=str(module_path)
            ))
        
        if not structure["has_init"]:
            self.issues.append(CodeIssue(
                level=IssueLevel.ERROR,
                message="Missing __init__.py file",
                file_path=str(module_path)
            ))
        
        return structure

    def _analyze_manifest(self, module_path: Path) -> Dict[str, Any]:
        """Analyze __manifest__.py file"""
        manifest_path = module_path / "__manifest__.py"
        
        if not manifest_path.exists():
            return {"error": "Manifest file not found"}
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse manifest as Python dict
            manifest_dict = ast.literal_eval(content)
            
            analysis = {
                "content": manifest_dict,
                "compliance": self._check_manifest_compliance(manifest_dict, str(manifest_path))
            }
            
            return analysis
            
        except Exception as e:
            self.issues.append(CodeIssue(
                level=IssueLevel.ERROR,
                message=f"Error parsing manifest: {str(e)}",
                file_path=str(manifest_path)
            ))
            return {"error": f"Error parsing manifest: {str(e)}"}

    def _check_manifest_compliance(self, manifest: Dict, file_path: str) -> Dict[str, bool]:
        """Check manifest compliance with Odoo 18 standards"""
        compliance = {}
        
        # Check required keys
        for key in self.required_manifest_keys:
            is_present = key in manifest
            compliance[f"has_{key}"] = is_present
            
            if not is_present:
                self.issues.append(CodeIssue(
                    level=IssueLevel.ERROR,
                    message=f"Missing required manifest key: {key}",
                    file_path=file_path
                ))
        
        # Check recommended keys
        for key in self.recommended_manifest_keys:
            is_present = key in manifest
            compliance[f"has_{key}"] = is_present
            
            if not is_present:
                self.issues.append(CodeIssue(
                    level=IssueLevel.WARNING,
                    message=f"Missing recommended manifest key: {key}",
                    file_path=file_path
                ))
        
        # Version format check
        if 'version' in manifest:
            version = manifest['version']
            if not re.match(r'^\d+\.\d+(\.\d+)*$', version):
                self.issues.append(CodeIssue(
                    level=IssueLevel.WARNING,
                    message=f"Version format should follow semantic versioning: {version}",
                    file_path=file_path
                ))
        
        return compliance

    def _analyze_models(self, module_path: Path) -> List[Dict[str, Any]]:
        """Analyze model files in the models directory"""
        models_dir = module_path / "models"
        models_analysis = []
        
        if not models_dir.exists():
            return models_analysis
        
        for model_file in models_dir.glob("*.py"):
            if model_file.name == "__init__.py":
                continue
                
            analysis = self._analyze_model_file(model_file)
            if analysis:
                models_analysis.append(analysis)
        
        return models_analysis

    def _analyze_model_file(self, model_file: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single model file"""
        try:
            with open(model_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                "file": model_file.name,
                "classes": [],
                "imports": [],
                "compliance_score": 0
            }
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    analysis["imports"].append({
                        "module": node.module,
                        "names": [alias.name for alias in (node.names or [])]
                    })
            
            # Extract model classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_analysis = self._analyze_model_class(node, str(model_file))
                    if class_analysis:
                        analysis["classes"].append(class_analysis)
            
            return analysis
            
        except Exception as e:
            self.issues.append(CodeIssue(
                level=IssueLevel.ERROR,
                message=f"Error parsing model file: {str(e)}",
                file_path=str(model_file)
            ))
            return None

    def _analyze_model_class(self, class_node: ast.ClassDef, file_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a model class definition"""
        # Check if it's an Odoo model
        is_odoo_model = False
        model_name = None
        
        for node in ast.walk(class_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "_name":
                        if isinstance(node.value, ast.Constant):
                            model_name = node.value.value
                            is_odoo_model = True
        
        if not is_odoo_model:
            return None
        
        analysis = {
            "class_name": class_node.name,
            "model_name": model_name,
            "line_number": class_node.lineno,
            "fields": [],
            "methods": [],
            "inherits": []
        }
        
        # Check class naming convention
        if not self.odoo_patterns['class_naming'].match(class_node.name):
            self.issues.append(CodeIssue(
                level=IssueLevel.WARNING,
                message=f"Class name '{class_node.name}' doesn't follow PascalCase convention",
                file_path=file_path,
                line_number=class_node.lineno
            ))
        
        # Check model naming convention
        if model_name and not self.odoo_patterns['model_naming'].match(model_name):
            self.issues.append(CodeIssue(
                level=IssueLevel.WARNING,
                message=f"Model name '{model_name}' doesn't follow dot notation convention",
                file_path=file_path,
                line_number=class_node.lineno
            ))
        
        # Analyze fields and methods
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id.startswith('_'):
                            continue  # Skip private attributes
                        
                        # Check if it's a field
                        if isinstance(node.value, ast.Call):
                            if hasattr(node.value.func, 'attr') and 'fields' in str(node.value.func):
                                field_analysis = self._analyze_field(target.id, node, file_path)
                                analysis["fields"].append(field_analysis)
            
            elif isinstance(node, ast.FunctionDef):
                method_analysis = self._analyze_method(node, file_path)
                analysis["methods"].append(method_analysis)
        
        return analysis

    def _analyze_field(self, field_name: str, node: ast.Assign, file_path: str) -> Dict[str, Any]:
        """Analyze a model field definition"""
        field_analysis = {
            "name": field_name,
            "line_number": node.lineno,
            "type": "unknown",
            "attributes": {}
        }
        
        # Check field naming convention
        if not self.odoo_patterns['field_naming'].match(field_name):
            self.issues.append(CodeIssue(
                level=IssueLevel.WARNING,
                message=f"Field name '{field_name}' doesn't follow snake_case convention",
                file_path=file_path,
                line_number=node.lineno
            ))
        
        # Extract field type and attributes
        if isinstance(node.value, ast.Call):
            if hasattr(node.value.func, 'attr'):
                field_analysis["type"] = node.value.func.attr
            
            # Extract field attributes from keywords
            for keyword in node.value.keywords:
                if isinstance(keyword.value, ast.Constant):
                    field_analysis["attributes"][keyword.arg] = keyword.value.value
        
        return field_analysis

    def _analyze_method(self, method_node: ast.FunctionDef, file_path: str) -> Dict[str, Any]:
        """Analyze a model method"""
        method_analysis = {
            "name": method_node.name,
            "line_number": method_node.lineno,
            "decorators": [],
            "args": [arg.arg for arg in method_node.args.args]
        }
        
        # Check method naming convention
        if not method_node.name.startswith('_') and not self.odoo_patterns['method_naming'].match(method_node.name):
            self.issues.append(CodeIssue(
                level=IssueLevel.WARNING,
                message=f"Method name '{method_node.name}' doesn't follow snake_case convention",
                file_path=file_path,
                line_number=method_node.lineno
            ))
        
        # Extract decorators
        for decorator in method_node.decorator_list:
            if isinstance(decorator, ast.Name):
                method_analysis["decorators"].append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                method_analysis["decorators"].append(f"{decorator.value.id}.{decorator.attr}")
        
        return method_analysis

    def _analyze_views(self, module_path: Path) -> List[Dict[str, Any]]:
        """Analyze XML view files"""
        views_dir = module_path / "views"
        views_analysis = []
        
        # Check both views directory and root for XML files
        xml_locations = [views_dir]
        if not views_dir.exists():
            xml_locations = [module_path]
        
        for location in xml_locations:
            if location.exists():
                for xml_file in location.glob("*.xml"):
                    analysis = self._analyze_view_file(xml_file)
                    if analysis:
                        views_analysis.append(analysis)
        
        return views_analysis

    def _analyze_view_file(self, xml_file: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single XML view file"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            analysis = {
                "file": xml_file.name,
                "records": [],
                "view_count": 0,
                "menu_count": 0,
                "action_count": 0
            }
            
            # Analyze records
            for record in root.findall(".//record"):
                record_analysis = {
                    "id": record.get("id"),
                    "model": record.get("model"),
                    "fields": []
                }
                
                # Count different types
                if record.get("model") and "view" in record.get("model", ""):
                    analysis["view_count"] += 1
                elif record.get("model") and "menu" in record.get("model", ""):
                    analysis["menu_count"] += 1
                elif record.get("model") and "action" in record.get("model", ""):
                    analysis["action_count"] += 1
                
                # Extract fields
                for field in record.findall("field"):
                    record_analysis["fields"].append({
                        "name": field.get("name"),
                        "value": field.text or field.get("ref")
                    })
                
                analysis["records"].append(record_analysis)
            
            return analysis
            
        except ET.ParseError as e:
            self.issues.append(CodeIssue(
                level=IssueLevel.ERROR,
                message=f"XML parse error: {str(e)}",
                file_path=str(xml_file)
            ))
            return None

    def _analyze_controllers(self, module_path: Path) -> List[Dict[str, Any]]:
        """Analyze controller files"""
        controllers_dir = module_path / "controllers"
        controllers_analysis = []
        
        if not controllers_dir.exists():
            return controllers_analysis
        
        for controller_file in controllers_dir.glob("*.py"):
            if controller_file.name == "__init__.py":
                continue
                
            analysis = self._analyze_controller_file(controller_file)
            if analysis:
                controllers_analysis.append(analysis)
        
        return controllers_analysis

    def _analyze_controller_file(self, controller_file: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single controller file"""
        try:
            with open(controller_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            analysis = {
                "file": controller_file.name,
                "classes": [],
                "routes": []
            }
            
            # Find controller classes and routes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_analysis = {"name": node.name, "methods": []}
                    
                    for method in node.body:
                        if isinstance(method, ast.FunctionDef):
                            # Check for route decorators
                            for decorator in method.decorator_list:
                                if isinstance(decorator, ast.Call) and \
                                   hasattr(decorator.func, 'attr') and \
                                   decorator.func.attr == 'route':
                                    route_info = {
                                        "method": method.name,
                                        "line": method.lineno,
                                        "route": "unknown"
                                    }
                                    
                                    if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                        route_info["route"] = decorator.args[0].value
                                    
                                    analysis["routes"].append(route_info)
                            
                            class_analysis["methods"].append({
                                "name": method.name,
                                "line": method.lineno
                            })
                    
                    analysis["classes"].append(class_analysis)
            
            return analysis
            
        except Exception as e:
            self.issues.append(CodeIssue(
                level=IssueLevel.ERROR,
                message=f"Error parsing controller file: {str(e)}",
                file_path=str(controller_file)
            ))
            return None

    def _analyze_security(self, module_path: Path) -> Dict[str, Any]:
        """Analyze security files"""
        security_dir = module_path / "security"
        security_analysis = {
            "has_security_dir": security_dir.exists(),
            "access_files": [],
            "rule_files": [],
            "group_files": []
        }
        
        if not security_dir.exists():
            self.issues.append(CodeIssue(
                level=IssueLevel.INFO,
                message="No security directory found - consider adding access control",
                file_path=str(module_path)
            ))
            return security_analysis
        
        # Analyze CSV access files
        for csv_file in security_dir.glob("*.csv"):
            security_analysis["access_files"].append(csv_file.name)
        
        # Analyze XML security files
        for xml_file in security_dir.glob("*.xml"):
            if "rule" in xml_file.name.lower():
                security_analysis["rule_files"].append(xml_file.name)
            elif "group" in xml_file.name.lower():
                security_analysis["group_files"].append(xml_file.name)
        
        return security_analysis

    def generate_module_template(self, module_name: str, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate a complete Odoo module template"""
        templates = {}
        
        # Generate __manifest__.py
        templates["__manifest__.py"] = self._generate_manifest_template(module_name, config)
        
        # Generate __init__.py
        templates["__init__.py"] = self._generate_init_template(config)
        
        # Generate model template if requested
        if config.get("generate_model", False):
            templates[f"models/{config.get('model_file', 'main')}.py"] = \
                self._generate_model_template(config)
            templates["models/__init__.py"] = \
                f"from . import {config.get('model_file', 'main')}"
        
        # Generate view template if requested
        if config.get("generate_views", False):
            templates[f"views/{config.get('view_file', 'views')}.xml"] = \
                self._generate_view_template(config)
        
        # Generate security template if requested
        if config.get("generate_security", False):
            templates["security/ir.model.access.csv"] = \
                self._generate_access_template(config)
        
        return templates

    def _generate_manifest_template(self, module_name: str, config: Dict[str, Any]) -> str:
        """Generate __manifest__.py template"""
        manifest = {
            'name': config.get('name', module_name.replace('_', ' ').title()),
            'version': config.get('version', '18.0.1.0.0'),
            'category': config.get('category', 'Custom'),
            'summary': config.get('summary', f'{module_name} module'),
            'description': config.get('description', f'Custom module: {module_name}'),
            'author': config.get('author', 'Your Company'),
            'depends': config.get('depends', ['base']),
            'data': [],
            'installable': True,
            'application': config.get('application', False),
            'auto_install': False,
            'license': config.get('license', 'LGPL-3'),
        }
        
        # Add data files based on generation options
        if config.get("generate_security", False):
            manifest['data'].append('security/ir.model.access.csv')
        
        if config.get("generate_views", False):
            manifest['data'].append(f"views/{config.get('view_file', 'views')}.xml")
        
        return f"# -*- coding: utf-8 -*-\n{{\n" + \
               "\n".join(f"    {repr(k)}: {repr(v)}," for k, v in manifest.items()) + \
               "\n}"

    def _generate_init_template(self, config: Dict[str, Any]) -> str:
        """Generate __init__.py template"""
        imports = []
        
        if config.get("generate_model", False):
            imports.append("from . import models")
        
        if config.get("generate_controllers", False):
            imports.append("from . import controllers")
        
        return "# -*- coding: utf-8 -*-\n" + "\n".join(imports)

    def _generate_model_template(self, config: Dict[str, Any]) -> str:
        """Generate model template"""
        model_name = config.get('model_name', 'custom.model')
        class_name = config.get('class_name', 'CustomModel')
        
        template = f'''# -*- coding: utf-8 -*-

from odoo import models, fields, api


class {class_name}(models.Model):
    _name = '{model_name}'
    _description = '{config.get("model_description", "Custom Model")}'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    # Computed fields
    display_name = fields.Char(string='Display Name', compute='_compute_display_name')
    
    # Relations
    # partner_id = fields.Many2one('res.partner', string='Partner')
    
    @api.depends('name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.name or 'New'
    
    @api.model_create_multi
    def create(self, vals_list):
        return super({class_name}, self).create(vals_list)
    
    def write(self, vals):
        return super({class_name}, self).write(vals)
    
    def unlink(self):
        return super({class_name}, self).unlink()
'''
        
        return template

    def _generate_view_template(self, config: Dict[str, Any]) -> str:
        """Generate XML view template"""
        model_name = config.get('model_name', 'custom.model')
        view_prefix = model_name.replace('.', '_')
        
        template = f'''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Tree View -->
    <record id="{view_prefix}_tree" model="ir.ui.view">
        <field name="name">{model_name}.tree</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="description"/>
                <field name="active"/>
            </tree>
        </field>
    </record>

    <!-- Form View -->
    <record id="{view_prefix}_form" model="ir.ui.view">
        <field name="name">{model_name}.form</field>
        <field name="model">{model_name}</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="active"/>
                    </group>
                    <group>
                        <field name="description"/>
                    </group>
                </sheet>
                <div class="oe_chatter">
                    <field name="message_follower_ids" widget="mail_followers"/>
                    <field name="activity_ids" widget="mail_activity"/>
                    <field name="message_ids" widget="mail_thread"/>
                </div>
            </form>
        </field>
    </record>

    <!-- Action -->
    <record id="{view_prefix}_action" model="ir.actions.act_window">
        <field name="name">{config.get("name", "Custom Model")}</field>
        <field name="res_model">{model_name}</field>
        <field name="view_mode">tree,form</field>
    </record>

    <!-- Menu -->
    <menuitem id="{view_prefix}_menu" 
              name="{config.get("name", "Custom Model")}" 
              action="{view_prefix}_action"
              sequence="10"/>
</odoo>
'''
        
        return template

    def _generate_access_template(self, config: Dict[str, Any]) -> str:
        """Generate access rights CSV template"""
        model_name = config.get('model_name', 'custom.model')
        model_clean = model_name.replace('.', '_')
        
        template = f'''id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_{model_clean}_user,{model_name} User,model_{model_clean},base.group_user,1,1,1,1
access_{model_clean}_manager,{model_name} Manager,model_{model_clean},base.group_system,1,1,1,1
'''
        
        return template

    def create_module(self, module_name: str, config: Dict[str, Any]) -> bool:
        """Create a complete Odoo module based on configuration"""
        module_path = self.addons_path / module_name
        
        if module_path.exists():
            self.issues.append(CodeIssue(
                level=IssueLevel.ERROR,
                message=f"Module {module_name} already exists",
                file_path=str(module_path)
            ))
            return False
        
        try:
            # Create module directory
            module_path.mkdir(parents=True)
            
            # Generate templates
            templates = self.generate_module_template(module_name, config)
            
            # Create files and directories
            for file_path, content in templates.items():
                full_path = module_path / file_path
                
                # Create parent directories if needed
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write file content
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return True
            
        except Exception as e:
            self.issues.append(CodeIssue(
                level=IssueLevel.ERROR,
                message=f"Error creating module: {str(e)}",
                file_path=str(module_path)
            ))
            return False

    def get_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Module structure recommendations
        if not analysis["structure"]["has_manifest"]:
            recommendations.append("Add __manifest__.py file with proper module metadata")
        
        if not analysis["structure"]["has_init"]:
            recommendations.append("Add __init__.py file with proper imports")
        
        # Model recommendations
        for model in analysis.get("models", []):
            for model_class in model["classes"]:
                if not model_class.get("fields"):
                    recommendations.append(f"Add fields to model {model_class['model_name']}")
                
                # Check for required methods
                method_names = [m["name"] for m in model_class["methods"]]
                if "create" not in method_names and "write" not in method_names:
                    recommendations.append(f"Consider adding create/write methods to {model_class['model_name']}")
        
        # Security recommendations
        security = analysis.get("security", {})
        if not security.get("has_security_dir"):
            recommendations.append("Add security directory with access control files")
        
        # View recommendations
        views = analysis.get("views", [])
        if not views:
            recommendations.append("Add XML views for better user experience")
        
        return recommendations

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive analysis report"""
        report_lines = [
            f"# Odoo Module Analysis Report",
            f"",
            f"**Module:** {analysis['module_name']}",
            f"**Path:** {analysis['path']}",
            f"**Analysis Date:** {os.popen('date').read().strip()}",
            f"",
            f"## Structure Overview",
        ]
        
        structure = analysis["structure"]
        report_lines.extend([
            f"- Manifest file: {'✓' if structure['has_manifest'] else '✗'}",
            f"- Init file: {'✓' if structure['has_init'] else '✗'}",
            f"- Directories: {', '.join(structure['directories'])}",
            f"- Python files: {len(structure['python_files'])}",
            f"- XML files: {len(structure['xml_files'])}",
            f"",
        ])
        
        # Models section
        models = analysis.get("models", [])
        if models:
            report_lines.extend([
                f"## Models ({len(models)} files)",
                f""
            ])
            
            for model in models:
                for model_class in model["classes"]:
                    report_lines.extend([
                        f"### {model_class['class_name']} ({model_class['model_name']})",
                        f"- Fields: {len(model_class['fields'])}",
                        f"- Methods: {len(model_class['methods'])}",
                        f""
                    ])
        
        # Views section
        views = analysis.get("views", [])
        if views:
            total_views = sum(v["view_count"] for v in views)
            total_menus = sum(v["menu_count"] for v in views)
            total_actions = sum(v["action_count"] for v in views)
            
            report_lines.extend([
                f"## Views ({len(views)} files)",
                f"- Total views: {total_views}",
                f"- Total menus: {total_menus}", 
                f"- Total actions: {total_actions}",
                f""
            ])
        
        # Issues section
        issues = analysis.get("issues", [])
        if issues:
            report_lines.extend([
                f"## Issues ({len(issues)})",
                f""
            ])
            
            for issue in issues:
                level_icon = {"error": "🚨", "warning": "⚠️", "info": "ℹ️", "suggestion": "💡"}.get(issue["level"], "")
                report_lines.append(f"- {level_icon} **{issue['level'].upper()}**: {issue['message']}")
                if issue.get("line_number"):
                    report_lines.append(f"  - Line {issue['line_number']}")
                if issue.get("suggestion"):
                    report_lines.append(f"  - Suggestion: {issue['suggestion']}")
            
            report_lines.append("")
        
        # Recommendations section
        recommendations = self.get_recommendations(analysis)
        if recommendations:
            report_lines.extend([
                f"## Recommendations",
                f""
            ])
            
            for rec in recommendations:
                report_lines.append(f"- {rec}")
        
        return "\n".join(report_lines)


def main():
    """CLI interface for the Odoo Agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Odoo 18 Development Agent")
    parser.add_argument("--project-path", default=".", help="Path to Odoo project")
    parser.add_argument("--analyze", help="Analyze a specific module")
    parser.add_argument("--create", help="Create a new module")
    parser.add_argument("--config", help="Configuration file for module creation")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    
    args = parser.parse_args()
    
    agent = OdooAgent(args.project_path)
    
    if args.analyze:
        print(f"Analyzing module: {args.analyze}")
        analysis = agent.analyze_module(args.analyze)
        
        if args.report:
            report = agent.generate_report(analysis)
            print(report)
        else:
            print(json.dumps(analysis, indent=2))
    
    elif args.create:
        config = {}
        if args.config and os.path.exists(args.config):
            with open(args.config, 'r') as f:
                config = json.load(f)
        
        print(f"Creating module: {args.create}")
        success = agent.create_module(args.create, config)
        
        if success:
            print(f"Module {args.create} created successfully!")
        else:
            print("Failed to create module. Check errors above.")
    
    else:
        print("Use --analyze <module_name> or --create <module_name>")


if __name__ == "__main__":
    main()