from mcp.types import (
    Implementation,
    InitializeResult,
    ServerCapabilities,
    ToolsCapability,
)

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class LLMMCPServerConfig(models.Model):
    _name = "llm.mcp.server.config"
    _description = "MCP Server Configuration"
    _inherit = ["mail.thread"]

    name = fields.Char(
        string="Server Name",
        required=True,
        default="Odoo LLM MCP Server",
        tracking=True,
    )
    version = fields.Char(
        string="Server Version",
        required=True,
        default="1.0.0",
        tracking=True,
    )
    latest_protocol_version = fields.Char(
        string="Latest Protocol Version",
        required=True,
        help="The latest/default protocol version this server supports",
        tracking=True,
    )
    supported_protocol_versions = fields.Json(
        string="Supported Protocol Versions",
        required=False,
        help="List of additional MCP protocol versions this server supports (excluding latest) in json array[str]",
        tracking=True,
    )
    all_supported_protocol_versions = fields.Json(
        string="All Supported Protocol Versions",
        compute="_compute_all_supported_protocol_versions",
        help="Complete list of all protocol versions (supported + latest)",
        store=False,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )
    external_url = fields.Char(
        string="External URL",
        help="External URL that Letta can reach (e.g., http://host.docker.internal:8069 for Docker). "
        "Leave empty to auto-detect from web.base.url",
        tracking=True,
    )

    # MCP Server Mode Configuration
    mode = fields.Selection(
        [
            ("stateless", "Stateless Mode"),
            ("stateful", "Stateful Mode"),
        ],
        default="stateful",
        required=True,
        tracking=True,
        help="Server operation mode",
    )

    @api.constrains("active")
    def _check_single_active_record(self):
        """Ensure only one config record can be active at a time"""
        if self.active:
            other_active = self.search([("id", "!=", self.id), ("active", "=", True)])
            if other_active:
                raise ValidationError(
                    "Only one MCP Server configuration can be active at a time."
                )

    @api.model
    def get_active_config(self):
        """Get the active MCP server configuration"""
        config = self.search([("active", "=", True)], limit=1)
        if not config:
            raise ValidationError("No active MCP Server configuration found.")
        return config

    def get_mcp_server_url(self):
        """Get the MCP server URL that external clients can reach"""
        if self.external_url:
            return f"{self.external_url.rstrip('/')}/mcp"
        else:
            base_url = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("web.base.url", "http://localhost:8069")
            )
            return f"{base_url}/mcp"

    def handle_initialize_request(self, client_info=None, protocol_version=None):
        """Handle MCP initialize request - return MCP InitializeResult"""
        server_info = Implementation(name=self.name, version=self.version)

        return InitializeResult(
            protocolVersion=protocol_version,
            capabilities=self._get_server_capabilities(),
            serverInfo=server_info,
        )

    def _get_server_capabilities(self):
        """Get server capabilities based on configuration"""
        capabilities = ServerCapabilities(tools=ToolsCapability(listChanged=False))
        return capabilities

    @api.depends("latest_protocol_version", "supported_protocol_versions")
    def _compute_all_supported_protocol_versions(self):
        """Compute all supported protocol versions (supported + latest)"""
        for record in self:
            all_versions = []
            if record.latest_protocol_version:
                all_versions.append(record.latest_protocol_version)
            if record.supported_protocol_versions:
                all_versions.extend(record.supported_protocol_versions)
            # Remove duplicates while preserving order
            record.all_supported_protocol_versions = list(dict.fromkeys(all_versions))

    def is_protocol_version_supported(self, version):
        """Check if protocol version is supported"""
        if not version:
            return False
        return version in (self.all_supported_protocol_versions or [])

    def get_supported_versions_string(self):
        """Get comma-separated string of supported versions for error messages"""
        if not self.all_supported_protocol_versions:
            return "None configured"
        return ", ".join(self.all_supported_protocol_versions)

    def get_default_protocol_version(self):
        """Get the default protocol version (latest)"""
        return self.latest_protocol_version

    def get_health_status_data(self):
        """Get health status data - return plain dict"""
        return {
            "status": "healthy",
            "server": self.name,
            "version": self.version,
        }
