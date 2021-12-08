
from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    adavance_lines = fields.One2many('account.payment', 'purchase_order_id')

    def create_advance_payment(self):
        return {
            'name': 'Advance Payment',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'view_id': self.env.ref('account.view_account_payment_form').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_payment_type': 'outbound',
                'default_partner_id': self.partner_id.id,
                'default_partner_type': 'supplier',
                'search_default_inbound_filter': 1,
                'default_purchase_order_id': self.id,
                'default_purchase_order_visibility': True,
                'default_move_journal_types': ('bank', 'cash'),
            },

        }


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    purchase_order_id = fields.Many2one('purchase.order')
    purchase_order_visibility = fields.Boolean()