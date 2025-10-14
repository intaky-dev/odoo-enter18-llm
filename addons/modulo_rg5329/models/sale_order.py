from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def apply_rg5329_logic_manual(self):
        """Public method to manually trigger RG5329 logic"""
        return self._apply_rg5329_universal()
    
    def _apply_rg5329_universal(self):
        """
        UNIVERSAL RG5329 Logic - Sobrescribe toda lógica automática
        Se ejecuta en TODOS los eventos importantes
        """
        if self.state not in ['draft', 'sent']:
            return True
        
        # Calculate total
        total = sum(line.price_subtotal for line in self.order_line) or 0
        _logger.info("=== RG5329 UNIVERSAL: Order %s - Total $%s ===", self.name or 'New', total)
        
        # Find RG5329 tax (buscar por nombre también por si falla el campo)
        rg5329_tax = None
        
        # Try by custom field first
        try:
            rg5329_tax = self.env['account.tax'].sudo().search([
                ('is_rg5329_perception', '=', True)
            ], limit=1)
        except:
            pass
        
        # Fallback: search by name and amount
        if not rg5329_tax:
            all_taxes = self.env['account.tax'].sudo().search([
                ('type_tax_use', '=', 'sale'),
                ('amount', '>', 2.5),
                ('amount', '<', 4)
            ])
            for tax in all_taxes:
                if 'rg5329' in tax.name.lower() or 'percep' in tax.name.lower():
                    rg5329_tax = tax
                    break
        
        if not rg5329_tax:
            _logger.warning("RG5329 UNIVERSAL: No RG5329 tax found!")
            return False
        
        _logger.info("RG5329 UNIVERSAL: Using tax %s (ID: %s)", rg5329_tax.name, rg5329_tax.id)
        
        # Check customer eligibility
        is_eligible = self._is_customer_eligible_simple()
        should_apply = is_eligible and total >= 100000
        
        _logger.info("RG5329 UNIVERSAL: Eligible=%s, Total>=100k=%s, ShouldApply=%s", 
                    is_eligible, total >= 100000, should_apply)
        
        # Apply/Remove to ALL lines - FORCE OVERRIDE
        changes_made = 0
        for line in self.order_line:
            if not line.product_id:
                continue
                
            has_rg5329 = rg5329_tax.id in line.tax_id.ids
            
            if should_apply and not has_rg5329:
                # ADD RG5329
                new_taxes = line.tax_id.ids + [rg5329_tax.id]
                line.sudo().write({'tax_id': [(6, 0, new_taxes)]})
                _logger.info("RG5329 UNIVERSAL: ✅ ADDED to line (total $%s >= 100k)", total)
                changes_made += 1
                
            elif not should_apply and has_rg5329:
                # REMOVE RG5329 - FORCE
                new_taxes = [t for t in line.tax_id.ids if t != rg5329_tax.id]
                line.sudo().write({'tax_id': [(6, 0, new_taxes)]})
                _logger.info("RG5329 UNIVERSAL: ❌ REMOVED from line (total $%s < 100k or not eligible)", total)
                changes_made += 1
        
        if changes_made > 0:
            _logger.info("RG5329 UNIVERSAL: Made %d tax changes", changes_made)
        
        return True
    
    def _is_customer_eligible_simple(self):
        """Simple eligibility check"""
        try:
            partner = self.partner_id
            if not partner or not hasattr(partner, 'l10n_ar_afip_responsibility_type_id'):
                return False
            
            if not partner.l10n_ar_afip_responsibility_type_id:
                return False
            
            return partner.l10n_ar_afip_responsibility_type_id.code == '1'
        except:
            return False
    
    # Override MULTIPLE calculation points to ensure our logic always runs
    
    def _compute_amounts(self):
        """Override amounts calculation - MOST IMPORTANT"""
        result = super()._compute_amounts()
        self._apply_rg5329_universal()
        return result
    
    @api.onchange('order_line')
    def _onchange_order_line(self):
        """Override when order lines change"""
        result = super()._onchange_order_line()
        if not self.env.context.get('skip_rg5329'):
            self._apply_rg5329_universal()
        return result
    
    @api.onchange('partner_id')
    def _onchange_partner_id_rg5329(self):
        """Override when partner changes"""
        if self.partner_id:
            self._apply_rg5329_universal()

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    def write(self, vals):
        """Override write - CRÍTICO para cambios de cantidad"""
        result = super().write(vals)
        
        # FORCE trigger on ANY quantity or price change
        if 'product_uom_qty' in vals or 'price_unit' in vals:
            for line in self:
                if line.order_id and line.order_id.state in ['draft', 'sent']:
                    _logger.info("RG5329 UNIVERSAL: Line write triggered - qty/price changed")
                    # FORCE run our logic
                    line.order_id.with_context(skip_rg5329=False)._apply_rg5329_universal()
                    
        return result
    
    @api.onchange('product_uom_qty', 'price_unit', 'product_id')
    def _onchange_product_uom_qty_rg5329(self):
        """Override when quantity/price changes in UI"""
        if self.order_id:
            _logger.info("RG5329 UNIVERSAL: Line onchange triggered")
            self.order_id._apply_rg5329_universal()
    
    def create(self, vals_list):
        """Override create to trigger on new lines"""
        result = super().create(vals_list)
        for line in result:
            if line.order_id and line.order_id.state in ['draft', 'sent']:
                line.order_id._apply_rg5329_universal()
        return result