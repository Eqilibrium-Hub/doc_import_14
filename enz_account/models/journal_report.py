from odoo import fields, models, api
from datetime import datetime


class JournalReport(models.Model):
    _name = 'journal.report'

    from_date = fields.Date("From date", default=datetime.today())
    to_date = fields.Date("To date", default=datetime.today())
    type = fields.Selection([('yes', 'Yes'), ('no', 'NO')],
                            string='Expense', default='yes')
    all_from = fields.Boolean("All")
    all = fields.Boolean("All")
    from_account_type = fields.Many2one('account.account.type', 'From Account Type')
    from_account = fields.Many2one('account.account', "From Account",
                                   domain="[('user_type_id', '=', from_account_type)]")
    account_type = fields.Many2one('account.account.type', 'To Account Type')
    account = fields.Many2one('account.account', "To Account", domain="[('user_type_id', '=', account_type)]")
    rec_id = fields.One2many('journal.records', 'report_id')

    @api.onchange('from_account', 'account', 'all', 'all_from', 'account_type')
    def onchnage_from_account(self):
        complete_list = []
        self.rec_id = False
        if self.type == 'no':
            if self.all_from == False:
                print("all_from = false")
                if self.from_account and self.account:
                    # if self.all_from == False:
                    # complete_list = []

                    # final_accounts = accounts.line_ids.filtered(lambda a: a.account_id == self.account).mapped('move_id')
                    moves = self.env['account.move.line'].search([('account_id', '=', self.from_account.id)]).mapped(
                        'move_id')
                    final_move = moves.line_ids.filtered(lambda a: a.account_id == self.account).mapped('move_id')

                    for m_id in final_move:
                        if m_id.date >= self.from_date and m_id.date <= self.to_date:
                            for l in m_id.line_ids:
                                credit_dict = (0, 0, {
                                    'account': l.account_id.id,
                                    'partner': l.partner_id.id,
                                    'debit': l.debit,
                                    'credit': l.credit,
                                    'label': l.name,
                                    'journal': m_id.journal_id.id,
                                    'reference': m_id.ref
                                })
                                complete_list.append(credit_dict)
                    self.rec_id = complete_list
            if self.all_from == True:
                print("all_from = true")
                moves = self.env['account.move.line'].search(
                    [('account_id.user_type_id', '=', self.from_account_type.id)]).mapped(
                    'move_id')
                print("moves = ", moves)
                final_move = moves.line_ids.filtered(lambda a: a.account_id.user_type_id == self.account_type).mapped(
                    'move_id')
                # complete_list = []
                print("new moves = ", final_move)
                for m_id in final_move:
                    if m_id.date >= self.from_date and m_id.date <= self.to_date:
                        for l in m_id.line_ids:
                            credit_dict = (0, 0, {
                                'account': l.account_id.id,
                                'partner': l.partner_id.id,
                                'debit': l.debit,
                                'credit': l.credit,
                                'label': l.name,
                                'journal': m_id.journal_id.id,
                                'reference': m_id.ref
                            })
                            complete_list.append(credit_dict)
                self.rec_id = complete_list


        if self.type == 'yes':
            if self.all == False:
                print("all = false")
                credit_lines = self.env['account.move.line'].search([('account_id', '=', self.account.id)]).mapped(
                    'move_id')
                final_move = credit_lines.line_ids.mapped('move_id')
                for i in final_move:
                    if i.date >= self.from_date and i.date <= self.to_date:
                        for l in i.line_ids:
                            credit_dict = (0, 0, {
                                'account': l.account_id.id,
                                'partner': l.partner_id.id,
                                'debit': l.debit,
                                'credit': l.credit,
                                'label': l.name,
                                'journal': i.journal_id.id,
                                'reference': i.ref
                            })
                            complete_list.append(credit_dict)
                self.rec_id = complete_list


            if self.all == True:
                print("all = true")
                credit_lines = self.env['account.move.line'].search([('account_id.user_type_id', '=', self.account_type.id)]).mapped(
                    'move_id')
                final_move = credit_lines.line_ids.mapped('move_id')
                for i in final_move:
                    if i.date >= self.from_date and i.date <= self.to_date:
                        for l in i.line_ids:
                            credit_dict = (0, 0, {
                                'account': l.account_id.id,
                                'partner': l.partner_id.id,
                                'debit': l.debit,
                                'credit': l.credit,
                                'label': l.name,
                                'journal': i.journal_id.id,
                                'reference': i.ref
                            })
                            complete_list.append(credit_dict)
                self.rec_id = complete_list

    @api.onchange('type')
    def type_change(self):
        if self.type == 'yes':
            pr_id = self.env['account.account.type'].search([('name', '=', 'Expenses')])
            self.account_type = pr_id
            if self.all_from == True:
                self.all_from = False
            print("all from",self.all_from)


        else:
            self.account_type = None
            if self.all == True:
                self.all = False
            print("all",self.all)

class JournalRecords(models.Model):
    _name = 'journal.records'

    report_id = fields.Many2one('journal.report')
    reference = fields.Char("Reference")
    journal = fields.Many2one('account.journal', "Journal")
    account = fields.Many2one('account.account', "Account")
    partner = fields.Many2one('res.partner', "Partner")
    label = fields.Char("Label")
    debit = fields.Monetary('Debit', store=True, help="Debit")
    credit = fields.Monetary('Credit', store=True, help="Credit")
    currency_id = fields.Many2one('res.currency', string="Company Currency",
                                  default=lambda self: self.env.company.currency_id,
                                  store=True)
