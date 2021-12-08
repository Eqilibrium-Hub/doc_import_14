# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date
from datetime import datetime
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError


class InventoryPurchaseSale(models.Model):
    _name = "inventory.purchase.sale"
    _order = "id desc, name desc"

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    create_date = fields.Date(string='Create Date', default=fields.Date.context_today, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    sale_id = fields.Many2one('sale.order', string="Sale Order")
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    product_id = fields.Many2one('product.product', string="Product")
    purchase_qty = fields.Float('Purchased Qty')
    sale_qty = fields.Float('Sale Qty')
    onhand_qty = fields.Float('O Qty')
    current_qty = fields.Float('C Qty')
    company_id = fields.Many2one('res.company', string="Company Id")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'inventory.purchase.sale') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('inventory.purchase.sale') or _('New')
        return super(InventoryPurchaseSale, self).create(vals)

    def action_show_history(self):
            total_ledgers = self.env['inventory.po.so.partner'].search([('product_id','=',self.product_id.id)])
            action_vals = {
                'name': ('Report'),
                'domain': [('id', 'in', total_ledgers.ids)],
                'view_type': 'form',
                'res_model': 'inventory.po.so.partner',
                'view_id': False,
                'type': 'ir.actions.act_window',
            }
            if len(total_ledgers) == 1:
                action_vals.update({'res_id': total_ledgers[0].id, 'view_mode': 'tree'})
            else:
                action_vals['view_mode'] = 'tree'
            return action_vals


class InventoryPoSoPartner(models.Model):
    _name = "inventory.po.so.partner"
    _order = "id desc, name desc"

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    create_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    sale_id = fields.Many2one('sale.order', string="Sale Order")
    partner_id = fields.Many2one('res.partner',string="Description")
    partner_ref = fields.Integer(string="VCh No")
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")
    product_id = fields.Many2one('product.product', string="Product")
    purchase_qty = fields.Float('Inwards')
    sale_qty = fields.Float('Outwards')
    current_qty = fields.Float('C Qty')
    # company_id = fields.Many2one('res.company', string="Company Id")
    onhand_qty = fields.Float('O Qty')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'inventory.po.so.partner') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('inventory.po.so.partner') or _('New')
        return super(InventoryPoSoPartner, self).create(vals)
