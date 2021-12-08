from odoo import models,fields

class Templates(models.Model):
    _name = 'templates'
    _rec_name = 'name'

    name = fields.Char('Name')