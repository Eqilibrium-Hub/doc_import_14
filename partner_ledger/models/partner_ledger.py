# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, pycompat, float_repr
from odoo.tests.common import Form

from datetime import datetime
from lxml import etree
from PyPDF2 import PdfFileReader
from collections import namedtuple

import io
import base64
from odoo.exceptions import UserError, ValidationError


class PartnerLedgerCustom(models.Model):
    _name = 'partner.ledger.customer'

    date = fields.Date('Date')
    paid_date = fields.Date('Paid Date')
    address = fields.Text('Address')
    account = fields.Many2one('account.account')
    account_journal = fields.Many2one('account.journal')
    sale_id = fields.Many2one('sale.order', string="Sale")
    invoice_id = fields.Many2one('account.move', string='Invoice No')
    account_move = fields.Many2one('account.move.line', string='Account Move')
    product_id = fields.Many2one('product.product', string='Product Name')
    partner_id = fields.Many2one('res.partner', string='Partner')
    company_id = fields.Many2one('res.company', string='company')
    description = fields.Text(string='Description')
    uom = fields.Many2one('uom.uom', string='UoM')
    price_units = fields.Float('Unit')
    rate = fields.Float('Rate')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    balance = fields.Float('Balance')
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'),
                              ('10', 'October'), ('11', 'November'), ('12', 'December')])






##############OPening Bal###############3
class OpeningBalanceCustomers(models.Model):
    _inherit = "opening.balance.customers"
    _order = "name desc"


    def action_opening_bal(self):
        result = super(OpeningBalanceCustomers, self).action_opening_bal()
        for line in self.op_lines:
            if self.type_of_partner == 'partner':
                balance_amount =0
                journal = self.env['account.journal'].search(
                    [('name', '=', 'Miscellaneous Operations'), ('company_id', '=', self.company_id.id)]).id,
                previous = self.env['partner.ledger.customer'].search(
                    [('company_id', '=', self.company_id.id), ('partner_id', '=', line.partner_id.id)])
                if previous:
                    balance_amount = self.env['partner.ledger.customer'].search(
                        [('company_id', '=', self.company_id.id), ('partner_id', '=', line.partner_id.id)])[-1].balance

                self.env['partner.ledger.customer'].sudo().create({
                    'date': datetime.today().date(),
                    # 'invoice_id': self.id,
                    'description': 'Opening Balance',
                    'partner_id': line.partner_id.id,
                    # 'product_id': line.product_id.id,
                    'company_id': self.company_id.id,
                    'month': str(datetime.today().date().month),
                    'account_journal': journal,
                    # 'account_move': self.move_id.id,
                    'debit': line.op_amount,
                    'balance': line.op_amount + balance_amount,
                })
            else:
                balance_amount =0
                journal = self.env['account.journal'].search(
                    [('name', '=', 'Miscellaneous Operations'), ('company_id', '=', self.company_id.id)]).id,
                balance_amount += self.env['supplier.ledger.customer'].search(
                    [('partner_id', '=', line.partner_id.id), ('company_id', '=', self.company_id.id),
                     ('description', '=', 'Opening Balance')]).balance
                if self.env['supplier.ledger.customer'].search(
                        [('company_id', '=', self.company_id.id), ('partner_id', '=', line.partner_id.id)]):
                    balance_amount = self.env['supplier.ledger.customer'].search(
                        [('company_id', '=', self.company_id.id), ('partner_id', '=', line.partner_id.id)])[
                        -1].balance
                self.env['supplier.ledger.customer'].sudo().create({
                    'date': datetime.today().date(),
                    'partner_id': line.partner_id.id,
                    'description': 'Opening Balance',
                    # 'invoice_id': self.invoice_ids.id or False,
                    'company_id': self.company_id.id,
                    'credit':line.op_amount,
                    'debit': 0,
                    'month': str(datetime.today().date().month),
                    'balance': balance_amount-line.op_amount

                })

        return result


class PartnerLedgerReport(models.Model):
    _name = "partner.ledger.report"

    name = fields.Char("Name", index=True, default=lambda self: _('New'))
    sequence = fields.Integer(index=True)
    payment_date = fields.Date(string='Create Date', default=fields.Date.context_today, required=True, copy=False)
    from_date = fields.Date(string='From Date', copy=False, default=fields.Date.context_today, )
    to_date = fields.Date(string='To Date', copy=False, default=fields.Date.context_today, )
    report_lines = fields.One2many('sale.report.custom.line', 'report_line')
    partner_id = fields.Many2one('res.partner', string='Party Wise')
    company_id = fields.Many2one('res.company', string='Company',  index=True, default=lambda self: self.env.user.company_id)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'partner.ledger.report') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('partner.ledger.report') or _('New')
        return super(PartnerLedgerReport, self).create(vals)

    def print_report(self):
        if self.company_id:
            total_ledgers = self.env['partner.ledger.customer'].search(
                [('company_id', '=', self.company_id.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date),
                 ('partner_id', '=', self.partner_id.id)])
        else:
            total_ledgers = self.env['partner.ledger.customer'].search(
                [('date', '>=', self.from_date), ('date', '<=', self.to_date), ('partner_id', '=', self.partner_id.id)])
        action_vals = {
            'name': _(self.partner_id.name + '  ' + 'Ledger Report'),
            'domain': [('id', 'in', total_ledgers.ids)],
            'view_type': 'form',
            'res_model': 'partner.ledger.customer',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(total_ledgers) == 1:
            action_vals.update({'res_id': total_ledgers[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals


    def print_reports(self):
        return self.env.ref('partner_ledger.partner_ledger_customerss').report_action(self)

    def print_all(self):
        if self.company_id:
            total_ledgers = self.env['partner.ledger.customer'].search(
                [('company_id', '=', self.company_id.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date),
                 ('partner_id', '=', self.partner_id.id)])
            return total_ledgers
        else:
            total_ledgers = self.env['partner.ledger.customer'].search(
                [('date', '>=', self.from_date), ('date', '<=', self.to_date), ('partner_id', '=', self.partner_id.id)])

            return total_ledgers
