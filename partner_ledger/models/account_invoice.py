# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, pycompat, float_repr
from odoo.tests.common import Form

from datetime import datetime, date
from lxml import etree
from PyPDF2 import PdfFileReader
from collections import namedtuple

import io
import base64
from odoo.exceptions import UserError, ValidationError

DEFAULT_FACTURX_DATE_FORMAT = '%Y%m%d'


class AccountInvoice(models.Model):
    _inherit = 'account.move'


    def action_post(self):
        result = super(AccountInvoice, self).action_post()
        if self.move_type == 'out_invoice':
           self.create_product_profit()
           balance_amount = 0
           for line in self.invoice_line_ids:
               invoices = self.env['account.move'].search(
                   [('partner_id', '=', self.partner_id.id), ('company_id', '=', self.company_id.id),
                    ('payment_state', '!=', 'paid')])
               print("MOve ", invoices)
               if invoices.mapped('amount_residual'):
                   balance_amount = sum(invoices.mapped('amount_residual'))
                   print("2MOve ", invoices)
               else:
                   balance_amount = sum(invoices.mapped('amount_total'))
                   print("3MOve ", invoices)
               balance_amount += self.env['partner.ledger.customer'].search(
                   [('partner_id', '=', self.partner_id.id),('company_id','=',self.company_id.id), ('description', '=', 'Opening Balance')]).balance
               print("MOve ", balance_amount)
               Previous_led = self.env['partner.ledger.customer'].search(
                   [('company_id', '=', self.company_id.id), ('partner_id', '=', self.partner_id.id)])
               if Previous_led:
                   balance_amount = Previous_led[-1].balance + line.price_total + self.amount_tax
                   print("5MOve ", invoices)
               sale_ids = self.env['sale.order'].search([('invoice_ids', '=', self.id)]).id
               print(sale_ids)
               created = self.env['partner.ledger.customer'].sudo().create({
                   'date': datetime.today().date(),
                   'invoice_id': self.id,
                   'description': line.product_id.name,
                   'partner_id': self.partner_id.id,
                   'product_id': line.product_id.id,
                   'company_id': self.company_id.id,
                   'price_units': line.quantity,
                   'uom': line.product_id.uom_id.id,
                   'rate': line.price_unit,
                   'month':str(datetime.today().date().month),
                   'sale_id': self.env['sale.order'].search([('invoice_ids','=',self.id)]).id or False,
                   'account_journal': self.journal_id.id,
                   'account_move': self.invoice_line_ids.id,
                   'debit': line.price_total + self.amount_tax,
                   'balance': balance_amount,
               })
               print(created)

        if self.move_type == 'in_invoice':
            balance_amount = 0
            self.create_po_product_profit()
            for line in self.invoice_line_ids:

                invoices = self.env['account.move'].search(
                    [('partner_id', '=', self.partner_id.id),
                     ('company_id', '=', self.env.user.company_id.id), ('state', '!=', 'paid')])
                if invoices.mapped('amount_residual'):
                    balance_amount = sum(invoices.mapped('amount_residual'))
                else:
                    balance_amount = sum(invoices.mapped('amount_total'))

                Previous_led = self.env['supplier.ledger.customer'].search(
                    [('company_id', '=', self.company_id.id), ('partner_id', '=', self.partner_id.id)])
                if Previous_led:
                    # balance_amount = Previous_led[-1].balance + line.price_subtotal_signed + self.amount_tax
                    balance_amount = Previous_led[-1].balance + line.price_total

                self.env['supplier.ledger.customer'].sudo().create({
                    'date': datetime.today().date(),
                    'partner_id': self.partner_id.id,
                    'description': line.product_id.name,
                    'purchase_id': self.env['purchase.order'].search([('invoice_ids','=',self.id)]).id or False,
                    'invoice_id':self.id,
                    'month': str(datetime.today().date().month),
                    'company_id': self.company_id.id,
                    'product_id': line.product_id.id,
                    'price_units': line.quantity,
                    'uom': line.product_id.uom_id.id,
                    'rate': line.price_unit,
                    # 'credit': line.price_subtotal_signed + self.amount_tax,
                    'credit': self.amount_total,
                    'balance': balance_amount

                })
        return result

    def create_product_profit(self):
        for line in self.invoice_line_ids:
            old = self.env['purchase.profit.repo'].search([('product_id','=',line.product_id.id),('company_id','=',self.company_id.id)])
            if not old:
                self.env['purchase.profit.repo'].create({
                    # 'date':datetime.today().date(),
                    'company_id':self.company_id.id,
                    'product_id':line.product_id.id,
                    'sale_qty':line.quantity,
                    'sale_price':line.price_unit,
                    'sale_price_subtotal':line.price_subtotal,
                } )
            else:
                old.sale_qty += line.quantity
                old.sale_price += line.price_unit
                old.sale_price_subtotal += line.price_subtotal

    def create_po_product_profit(self):
        for line in self.invoice_line_ids:
            old = self.env['purchase.profit.repo'].search(
                [('product_id', '=', line.product_id.id), ('company_id', '=', self.company_id.id)])
            if not old:
                self.env['purchase.profit.repo'].create({
                    # 'date':datetime.today().date(),
                    'company_id': self.company_id.id,
                    'product_id': line.product_id.id,
                    'qty': line.quantity,
                    # 'uom':line.product_uom.id,
                    'price': line.price_unit,
                    'price_subtotal': line.price_subtotal,
                })
            else:
                old.qty += line.quantity
                old.price += line.price_unit
                old.price_subtotal += line.price_subtotal








