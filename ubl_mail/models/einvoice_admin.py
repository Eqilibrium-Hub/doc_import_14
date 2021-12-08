from odoo import fields,models

class EinvoiceAdmin(models.Model):
    _name = 'einvoice.admin'

    name = fields.Many2one('res.partner')
    email_id = fields.Char()