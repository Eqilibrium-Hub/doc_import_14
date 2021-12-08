# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date
from datetime import datetime
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    def button_confirm(self):
        for line in self.order_line:
            old_record = self.env['inventory.purchase.sale'].search([('product_id', '=', line.product_id.id)])
            if not old_record:
                self.env['inventory.purchase.sale'].create({
                    'purchase_id':self.id,
                    'company_id':self.company_id.id,
                    # 'partner_id':self.partner_id.id,
                    'product_id':line.product_id.id,
                    'purchase_qty':line.product_qty,
                    'onhand_qty':line.product_id.qty_available,
                    'current_qty':line.product_id.qty_available + line.product_qty
                })
            else:
                old_record.purchase_qty += line.product_qty
                old_record.current_qty = old_record.current_qty+line.product_qty
            old_record = self.env['inventory.purchase.sale'].search([('product_id', '=', line.product_id.id)])

            self.env['inventory.po.so.partner'].create({
                'purchase_id': self.id,
                'company_id': self.company_id.id,
                'partner_id':self.partner_id.id,
                'product_id': line.product_id.id,
                'purchase_qty': line.product_qty,
                'partner_ref': self.partner_id.id,
                'onhand_qty': line.product_id.qty_available,
                'current_qty': old_record.current_qty
            })
        return super(PurchaseOrder, self).button_confirm()

