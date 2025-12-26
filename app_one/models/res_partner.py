from odoo import fields, models
class ResPartner(models.Model):
    _inherit = 'res.partner'
    property_id = fields.Many2one('property')
    price = fields.Float(compute='_compute_price')
    def _compute_price(self):
        for rec in self:
            rec.price = rec.property_id.selling_price