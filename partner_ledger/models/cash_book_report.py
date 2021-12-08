# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT



class CashReportComp(models.Model):
    _name = "cash.report.custom"
    _description = "Cash Report"
    _order = "id desc"

    name = fields.Char("Name", index=True, default=lambda self: _('New'))
    sequence = fields.Integer(index=True)
    payment_date = fields.Date(string='Create Date', default=fields.Date.context_today, required=True, copy=False)
    from_date = fields.Date(string='From Date', copy=False, default=fields.Date.context_today, )
    to_date = fields.Date(string='To Date', copy=False, default=fields.Date.context_today, )
    report_lines = fields.One2many('cash.report.custom.line', 'report_line')
    report_d_lines = fields.One2many('cash.denomination.line', 'report_d_line')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'cash.report.custom') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('cash.report.custom') or _('New')
        return super(CashReportComp, self).create(vals)


    def print_reports(self):
        return self.env.ref('partner_ledger.cashbook_customers').report_action(self)



    @api.onchange('from_date', 'to_date', )
    def onchange_form_date(self):
        self.report_lines = False
        all = self.env['cash.book.info'].search([('company_id', '=', 1), ('date', '>=', self.from_date),
                                                 ('date', '<=', self.to_date)])

        self.report_lines = False
        today_total_cheques = []
        for each_coll in all:
            product_line = (0, 0, {
                'date': datetime.today().date(),
                'account_journal': each_coll.account_journal.id,
                # 'partner_id': each_coll.partner_id.id,
                'company_id': each_coll.company_id.id,
                'description': each_coll.description,
                'payment_type': each_coll.payment_type,
                'partner_type': each_coll.partner_type,
                'debit': each_coll.debit,
                'credit': each_coll.credit,
                'account': each_coll.account.id,
                'balance': each_coll.balance

            })
            today_total_cheques.append(product_line)
        self.report_lines = today_total_cheques
    #
    # @api.multi
    # def action_cheque_statement(self):
    #
    #     return self.env.ref('ezp_cash_collection.executive_cheque_collection_id1').report_action(self)


class CashDenominationLine(models.Model):
    _name = "cash.denomination.line"
    _description = "Cash denomination Line"

    report_d_line = fields.Many2one('cash.report.custom')
    name = fields.Char('Reference Name')
    money_note_no = fields.Integer('Amount')
    money_note = fields.Integer('Count')
    money_total = fields.Integer('Total Amount')

    @api.onchange('money_note_no', 'money_note')
    def onchange_money_note(self):
        self.money_total = self.money_note_no * self.money_note




class CashReportCompLine(models.Model):
    _name = "cash.report.custom.line"
    _description = "Cash Report Line"

    report_line = fields.Many2one('cash.report.custom')
    date = fields.Date('Date')
    account = fields.Many2one('account.account')
    account_journal = fields.Many2one('account.journal')
    partner_id = fields.Many2one('res.partner', string='Partner')
    company_id = fields.Many2one('res.company', string='company')
    description = fields.Text(string='Description')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    balance = fields.Float('Balance')
    payment_id = fields.Many2one('account.payment')
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')])
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type')
