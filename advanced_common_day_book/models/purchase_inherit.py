from odoo import fields, models, api

class PurchaseInheritDefault(models.Model):
    _inherit = 'purchase.order'

    default_id = fields.Boolean("Default", default=True)

    def action_create_invoice(self):
        res = super().action_create_invoice()
        move_id = self.env['account.move'].search([('id', '=', self.invoice_ids.id)])
        print(move_id)

        move_id.default_id = self.default_id


        return res

class AccountMoveInerit(models.Model):
    _inherit = "account.move"

    default_id = fields.Boolean("Default")


