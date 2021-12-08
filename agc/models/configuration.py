from odoo import fields,models

class DescriptionConfiguration(models.Model):
    _name = 'description.configuration'

    name = fields.Char(required=1)