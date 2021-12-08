# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date
from datetime import datetime
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
import calendar


class OpeningBalanceCustomers(models.Model):
    _name = "opening.balance.customers"
    _order = "id desc, name desc"

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    start_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    op_lines = fields.One2many('opening.balance.lines', 'op_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('close', 'Closed'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3,
        default='draft')
    type_of_partner = fields.Selection([
        ('partner', 'Customer'),
        ('vendor', 'Vendor'),
    ], string='Type Of Partner', copy=False, index=True, track_visibility='onchange', track_sequence=3,
        default='partner')
    type_of_credit = fields.Boolean(string='Credit')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'opening.balance.customers') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('opening.balance.customers') or _('New')
        return super(OpeningBalanceCustomers, self).create(vals)

    def action_opening_bal_all(self):
        for l in self.env['opening.balance.customers'].search([('state', '=', 'draft')]):
            l.action_opening_bal()

    def action_opening_bal(self):
        self.write({'state': 'close'})
        for line in self.op_lines:
            vals = {
                'journal_id': self.env['account.journal'].search(
                    [('name', '=', 'Miscellaneous Operations'), ('company_id', '=', self.company_id.id)]).id,
                'state': 'draft',
                'ref': line.partner_id.name + 'Opening Balance'
            }
            pay_id_list = []
            move_id = self.env['account.move'].create(vals)
            partner_id = line.partner_id.id
            label = 'Opening Balance' + '/' + line.partner_id.name

            if self.type_of_partner == 'partner':
                if self.type_of_credit == False:

                    temp = (0, 0, {
                        'account_id': self.env['account.account'].search(
                            [('name', '=', 'Account Receivable'), ('company_id', '=', self.company_id.id)]).id,
                        'name': label,
                        'move_id': move_id.id,
                        'date': datetime.today().date(),
                        'partner_id': partner_id,
                        'debit': line.op_amount,
                        'credit': 0,
                    })
                    pay_id_list.append(temp)

                    acc = self.env['account.account'].search(
                        [('name', '=', 'Undistributed Profits/Losses'), ('company_id', '=', self.company_id.id)])
                    temp = (0, 0, {
                        'account_id': acc.id,
                        'name': label,
                        'move_id': move_id.id,
                        'date': datetime.today().date(),
                        'partner_id': partner_id,
                        'debit': 0,
                        'credit': line.op_amount,
                    })
                    pay_id_list.append(temp)
                    move_id.line_ids = pay_id_list
                    move_id.action_post()
                else:
                    temp = (0, 0, {
                        'account_id': self.env['account.account'].search(
                            [('name', '=', 'Account Payable'), ('company_id', '=', self.company_id.id)]).id,
                        'name': label,
                        'move_id': move_id.id,
                        'date': datetime.today().date(),
                        'partner_id': partner_id,
                        'debit': 0,
                        'credit': line.op_amount,
                    })
                    pay_id_list.append(temp)

                    acc = self.env['account.account'].search(
                        [('name', '=', 'Undistributed Profits/Losses'), ('company_id', '=', self.company_id.id)])
                    temp = (0, 0, {
                        'account_id': acc.id,
                        'name': label,
                        'move_id': move_id.id,
                        'date': datetime.today().date(),
                        'partner_id': partner_id,
                        'debit': line.op_amount,
                        'credit': 0,
                    })
                    pay_id_list.append(temp)
                    move_id.line_ids = pay_id_list
                    move_id.action_post()

            else:
                temp = (0, 0, {
                    'account_id': self.env['account.account'].search(
                        [('name', '=', 'Account Payable'), ('company_id', '=', self.company_id.id)]).id,
                    'name': label,
                    'move_id': move_id.id,
                    'date': datetime.today().date(),
                    'partner_id': partner_id,
                    'debit': 0,
                    'credit': line.op_amount,
                })
                pay_id_list.append(temp)

                # acc = self.env['account.account'].search(
                #     [('name', '=', 'Purchase Expense'), ('company_id', '=', self.company_id.id)])
                acc = self.env['account.account'].search(
                    [('name', '=', 'Undistributed Profits/Losses'), ('company_id', '=', self.company_id.id)])
                temp = (0, 0, {
                    'account_id': acc.id,
                    'name': label,
                    'move_id': move_id.id,
                    'date': datetime.today().date(),
                    'partner_id': partner_id,
                    'debit': line.op_amount,
                    'credit': 0,
                })
                pay_id_list.append(temp)
                move_id.line_ids = pay_id_list
                move_id.action_post()


class OpeningBalanceLines(models.Model):
    _name = "opening.balance.lines"

    op_id = fields.Many2one('opening.balance.customers')
    partner_id = fields.Many2one('res.partner', string="Partner", )
    op_amount = fields.Float('Opening Balance')
    type_of_partner = fields.Selection([
        ('partner', 'Customer'),
        ('vendor', 'Vendor'),
    ], string='Type Of Partner', copy=False, index=True, track_visibility='onchange', track_sequence=3,
    )

    @api.onchange('type_of_partner')
    def onchance_type_of_partner(self):
        if self.type_of_partner == 'partner':
            # partners = self.env['res.partner'].search([('customer', '=', True)])
            partners = self.env['res.partner'].search([])
            if partners:
                return {'domain': {'partner_id': [('id', 'in', partners.ids)]}}

        if self.type_of_partner == 'vendor':
            # partners = self.env['res.partner'].search([('supplier', '=', True)])
            partners = self.env['res.partner'].search([])
            if partners:
                return {'domain': {'partner_id': [('id', 'in', partners.ids)]}}




class AccountPayment(models.Model):
    _inherit = 'account.payment'

    compute_invoice_amount = fields.Float('Balance Amount')

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_type == 'customer':
            if self.partner_id:
                # debit = sum(self.env['account.move.line'].search([('partner_id','=',self.partner_id.id)]).filtered(lambda a:a.account_id.name == 'Account Receivable').mapped('debit'))
                # credit = sum(self.env['account.move.line'].search([('partner_id','=',self.partner_id.id)]).filtered(lambda a:a.account_id.name == 'Account Receivable').mapped('credit'))
                # self.compute_invoice_amount = debit-credit
                debit = sum(self.env['account.move.line'].search([('partner_id','=',self.partner_id.id),('account_id','=',self.destination_account_id.id)]).mapped('debit'))
                credit = sum(self.env['account.move.line'].search([('partner_id','=',self.partner_id.id),('account_id','=',self.destination_account_id.id)]).mapped('credit'))
                self.compute_invoice_amount = debit-credit

                ##########India Db below ############################################################3
                # if self.env['account.move'].search(
                #         [('partner_id', '=', self.partner_id.id), ('company_id', '=', self.env.user.company_id.id),
                #          ('state', '!=', 'paid')]).mapped('amount_residual'):
                #     self.compute_invoice_amount = sum(self.env['account.move'].search(
                #         [('partner_id', '=', self.partner_id.id), ('company_id', '=', self.env.user.company_id.id),
                #          ('state', '!=', 'paid')]).mapped('amount_residual'))
                #     # balance_amount += self.env['partner.ledger.customer'].search(
                #     #     [('partner_id', '=', self.partner_id.id), ('description', '=', 'Opening Balance')]).balance
                #     # Previous_led = self.env['partner.ledger.customer'].search(
                #     #     [('company_id', '=', self.company_id.id), ('partner_id', '=', self.partner_id.id)])
                #     # if Previous_led:
                #     #     self.compute_invoice_amount = Previous_led[-1].balance
                #
                #
                # else:
                #     self.compute_invoice_amount = sum(self.env['account.move'].search(
                #         [('partner_id', '=', self.partner_id.id), ('company_id', '=', self.env.user.company_id.id),
                #          ('state', '!=', 'paid')]).mapped('amount_total'))
                #     # Previous_led = self.env['partner.ledger.customer'].search(
                #     #     [('company_id', '=', self.company_id.id), ('partner_id', '=', self.partner_id.id)])
                #     # if Previous_led:
                #     #     self.compute_invoice_amount = Previous_led[-1].balance

            else:
                self.compute_invoice_amount =0
        else:
            if self.partner_id:
                # debit = sum(self.env['account.move.line'].search([('partner_id', '=', self.partner_id.id)]).filtered(
                #     lambda a: a.account_id.name == 'Account Payable').mapped('credit'))
                # credit = sum(self.env['account.move.line'].search([('partner_id', '=', self.partner_id.id)]).filtered(
                #     lambda a: a.account_id.name == 'Account Payable').mapped('debit'))
                # self.compute_invoice_amount = debit - credit
                debit = sum(self.env['account.move.line'].search([('partner_id', '=', self.partner_id.id),('account_id','=',self.destination_account_id.id)]).mapped('credit'))
                credit = sum(self.env['account.move.line'].search([('partner_id', '=', self.partner_id.id),('account_id','=',self.destination_account_id.id)]).mapped('debit'))
                self.compute_invoice_amount = debit - credit

            else:
                self.compute_invoice_amount = 0


