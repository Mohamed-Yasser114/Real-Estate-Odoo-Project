from odoo import  models, fields


class ChangeState(models.TransientModel):
    _name = 'change.state'
    property_id = fields.Many2one('property')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
    ])
    reason = fields.Char()
    def action_confirm(self):
        if self.state == 'closed':
            self.property_id_state = self.state
            self.property_id.create_history_record('closed', self.state, self.reason)
