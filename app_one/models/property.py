from datetime import timedelta
from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Property(models.Model):
    _name = 'property'
    _description = 'Property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    ref = fields.Char(default="New", readonly=True)
    create_time = fields.Datetime(default=fields.Datetime.now())
    next_time = fields.Datetime(compute='_compute_next_time')
    name = fields.Char(required=True)
    description = fields.Text(tracking=1)
    postcode = fields.Char(required=True,size=5)
    date_availability = fields.Date(tracking=1)
    expected_date = fields.Date(tracking = 1)
    is_late = fields.Boolean(default=False)
    expected_price = fields.Float()
    selling_price=fields.Float()
    diff = fields.Float(compute = "_compute_diff")
    bedrooms = fields.Integer()
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Float()
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
    ],default='north')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('sold', 'Sold'),
        ('closed','Closed')
    ], default="draft")
    owner_id = fields.Many2one('owner')
    tag_ids = fields.Many2many('tag')
    owner_address = fields.Char(related='owner_id.address', readonly=0)
    owner_phone = fields.Char(related='owner_id.phone', readonly=0)
    line_ids = fields.One2many('property.line', 'property_id')
    @api.constrains('bedrooms')
    def _check_bedrooms(self):
        for rec in self:
            if rec.bedrooms <= 0:
                raise  ValidationError('Please enter a valid number for bedrooms')
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, active_test=True) :
        res = super(Property, self)._search(args, offset=offset, limit=limit, order=order, active_test=active_test)
        return res
    def write(self, vals) :
        res = super(Property, self).write(vals)
        return  res
    def unlink(self):
        res = super(Property, self).unlink()
        return res
    def action_draft(self):
        for rec in self:
            rec.create_history_record(rec.state, 'draft')
            rec.state = 'draft'
    def action_pending(self):
        for rec in self:
            rec.create_history_record(rec.state, 'pending')
            rec.state = 'pending'
    def action_sold(self):
        for rec in self:
            rec.create_history_record(rec.state, 'sold')
            rec.state = 'sold'
    def action_closed(self):
        for rec in self:
            rec.create_history_record(rec.state, 'closed')
            rec.state = 'closed'
    def checking_expected_selling_date(self):
        property_ids = self.search([])
        for rec in property_ids:
            if rec.expected_date and rec.expected_date < fields.Date.today():
                rec.is_late = True
    @api.depends('expected_price', 'selling_price')
    def _compute_diff(self):
        for rec in self:
            rec.diff = rec.expected_price - rec.selling_price
    @api.onchange('expected_price')
    def _onchange_expected_price(self):
        for rec in  self:
            if rec.expected_price < 0:
                return {'warning':{
                    'title':'warning','message':'Please enter a valid price','type':'notification'
                }}
    @api.model
    def create(self, vals):
        res = super(Property, self).create(vals)
        if res.ref == "New":
            res.ref = self.env['ir.sequence'].next_by_code('property_seq')
        return res
    def create_history_record(self, old_state, new_state, reason=""):
        for rec in self:
            rec.env['property.history'].create({
                'user_id': rec.env.uid,
                'property_id': rec.id,
                'old_state': old_state,
                'new_state': new_state,
                'reason': reason or "",
                'line_ids' : [(0, 0, {'description': line.description, 'area': line.area}) for line in rec.line_ids],
            })
    def action_open_change_state_wizard(self):
        action = self.env['ir.actions.actions']._for_xml_id('app_one.change_state_wizard_action')
        action['context'] = {'default_property_id': self.id}
        return action
    @api.depends('create_time')
    def _compute_next_time(self):
        for rec in self:
            if rec.create_time:
                rec.next_time = rec.create_time + timedelta(hours=6)
            else:
                rec.next_time = False

    def action(self):
        print(self.env['property'].search([]))
    def action_open_related_owner(self):
        action = self.env['ir.actions.actions']._for_xml_id('app_one.owner_action')
        view_id = self.env.ref('app_one.owner_form_view').id
        action['res_id'] = self.owner_id.id
        action['views'] = [[view_id, 'form']]
        return  action

class PropertyLine(models.Model):
    _name = 'property.line'
    area = fields.Float()
    description = fields.Char()
    property_id = fields.Many2one('property')