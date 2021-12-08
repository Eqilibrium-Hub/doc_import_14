from odoo import fields, models, api

class StatementInherit(models.Model):
    _inherit = 'account.bank.statement'

    paid_amount = fields.Float("Amount")
