# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

from itertools import groupby
from datetime import datetime, date


class account_payment(models.Model):
    _inherit = "account.payment"

    # ref = fields.Char(required=1)

    #
    # def action_validate_invoice_payment(self):
    #    result = super(account_payment, self).action_validate_invoice_payment()
    #    for each in self:
    #        invoices = self.env['account.invoice'].search(
    #            [('partner_id', '=', self.partner_id.id), ('company_id', '=', self.company_id.id),
    #             ('state', '!=', 'paid')])
    #        if invoices.mapped('residual'):
    #            balance_amount = sum(invoices.mapped('residual'))
    #        else:
    #            balance_amount = sum(invoices.mapped('amount_total'))
    #        balance_amount += self.env['partner.ledger.customer'].search(
    #            [('partner_id', '=', self.partner_id.id), ('description', '=', 'Opening Balance')]).balance
    #        balance_amount = self.env['partner.ledger.customer'].search(
    #            [('company_id', '=', self.company_id.id), ('partner_id', '=', self.partner_id.id)])[
    #            -1].balance
    #        self.env['partner.ledger.customer'].create({
    #            'date': datetime.today().date(),
    #            'description':self.communication,
    #            'partner_id': self.partner_id.id,
    #            'invoice_id': self.invoice_ids.id or False,
    #            'company_id': self.company_id.id,
    #            'account_journal': self.journal_id.id,
    #            'account_move': self.mapped('move_line_ids').mapped('move_id').id,
    #            'credit': self.amount,
    #            'paid_date':datetime.today().date(),
    #            'balance': balance_amount-self.amount,
    #        })


    def action_post(self):
        result = super(account_payment, self).action_post()
        if self.payment_type == 'inbound':
            invoices = self.env['account.move'].search(
                [('partner_id', '=', self.partner_id.id), ('company_id', '=', self.company_id.id),
                 ('payment_state', '!=', 'paid')])
            print("payment", invoices)
            if invoices.mapped('amount_residual'):
                balance_amount = sum(invoices.mapped('amount_residual'))
            else:
                balance_amount = sum(invoices.mapped('amount_total'))
            balance_amount += self.env['partner.ledger.customer'].search(
                [('partner_id', '=', self.partner_id.id), ('company_id','=',self.company_id.id),('description', '=', 'Opening Balance')]).balance
            if self.env['partner.ledger.customer'].search(
                [('company_id', '=', self.company_id.id), ('partner_id', '=', self.partner_id.id)]):
                balance_amount = self.env['partner.ledger.customer'].search(
                    [('company_id', '=', self.company_id.id), ('partner_id', '=', self.partner_id.id)])[
                    -1].balance
                self.env['partner.ledger.customer'].sudo().create({
                    'date': datetime.today().date(),
                    # 'description': self.communication,
                    'month': str(datetime.today().date().month),
                    'partner_id': self.partner_id.id,
                    'invoice_id': self.move_id.id or False,
                    'company_id': self.company_id.id,
                    'account_journal': self.journal_id.id,
                    'account_move': self.mapped('invoice_line_ids').mapped('move_id').id,
                    'credit': self.amount,
                    'paid_date': datetime.today().date(),
                    'balance': balance_amount - self.amount,
                })
        if self.payment_type == 'outbound':
            balance_amount = 0
            invoices = self.env['account.move'].search(
                [('partner_id', '=', self.partner_id.id),
                 ('company_id', '=', self.env.user.company_id.id), ('payment_state', '!=', 'paid')])
            if invoices.mapped('amount_residual'):
                balance_amount = sum(invoices.mapped('amount_residual'))
            else:
                balance_amount = sum(invoices.mapped('amount_total'))
            balance_amount += self.env['supplier.ledger.customer'].search(
                [('partner_id', '=', self.partner_id.id),('company_id','=',self.company_id.id), ('description', '=', 'Opening Balance')]).balance
            if self.env['supplier.ledger.customer'].search(
                [('company_id', '=', self.company_id.id), ('partner_id', '=', self.partner_id.id)]):
                balance_amount = self.env['supplier.ledger.customer'].search(
                    [('company_id', '=', self.company_id.id), ('partner_id', '=', self.partner_id.id)])[
                    -1].balance
            self.env['supplier.ledger.customer'].sudo().create({
                'date': datetime.today().date(),
                'partner_id': self.partner_id.id,
                # 'description': self.communication,
                'invoice_id': self.move_id.id or False,
                'company_id': self.company_id.id,
                'debit': self.amount,
                'month': str(datetime.today().date().month),
                'balance': balance_amount - self.amount

            })
        if self.journal_id.type == 'cash':
            self.create_cash_book()

        return result

    def create_cash_book(self):
        # complete = sum(
        #     self.env['account.move.line'].search([('journal_id', '=', self.journal_id.id)]).mapped('debit'))
        credit_acc = self.env['account.journal'].search([('company_id','=',self.company_id.id),('type', '=', 'cash')]).payment_credit_account_id
        credit_complete = sum(self.env['account.move.line'].search([('company_id','=',self.company_id.id),('account_id', '=', credit_acc.id)]).mapped('credit'))
        debit_acc = self.env['account.journal'].search([('company_id','=',self.company_id.id),('type', '=', 'cash')]).payment_debit_account_id
        debit_complete = sum(self.env['account.move.line'].search([('company_id','=',self.company_id.id),('account_id', '=', debit_acc.id)]).mapped('debit'))
        complete_new = debit_complete-credit_complete
        debit = 0
        credit = 0
        acc = self.env['account.account']
        if self.payment_type == 'outbound':
           credit = self.amount
           # complete_new = complete - credit
        if self.payment_type == 'inbound':
           # complete_new = complete
           debit = self.amount
        acc = self.journal_id.payment_credit_account_id.id
        self.env['cash.book.info'].create({
            'date': datetime.today().date(),
            'account_journal': self.journal_id.id,
            'partner_id': self.partner_id.id,
            'company_id': self.company_id.id,
            'description': self.partner_id.name,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'debit': debit,
            'credit': credit,
            'account': acc,
            'payment_id': self.id,
            'balance': complete_new

        })
