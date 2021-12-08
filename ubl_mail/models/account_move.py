from odoo import fields,models

class AccountMove(models.Model):
    _inherit = "account.move"

    def _default_admin(self):
        default_id = self.env['einvoice.admin'].search([])
        if default_id:
            return default_id[-1].name
        else:
            return None

    admin_mail = fields.Many2one('res.partner',default=_default_admin)
