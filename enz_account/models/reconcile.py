from odoo import fields, models, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res_ids = super(AccountPayment, self).action_post()
        print("Working")
        journal_id = self.journal_id
        print(journal_id.name)
        amount, nb_lines_bank_account_balance = journal_id._get_journal_bank_account_balance()
        has_at_least_one_statement = journal_id.get_journal_dashboard_datas()
        # amt = has_at_least_one_statement['outstanding_pay_account_balance']
        last_journal = self.env['account.journal']
        outstanding_pay_account_balance, nb_lines_outstanding_pay_account_balance = journal_id._get_journal_outstanding_payments_account_balance(
            domain=[('move_id.state', '=', 'posted')])
        print(outstanding_pay_account_balance)
        print(amount)
        print(has_at_least_one_statement,"neww")
        print("bankaccountbalance",nb_lines_bank_account_balance)

        bank_amount = self.env['account.bank.statement'].search([('journal_id', '=', self.journal_id.id)])
        # bank_account_balance, nb_lines_bank_account_balance = journal_id._get_journal_bank_account_balance(
        #     domain=[('move_id.state', '=', 'posted')])
        # print("bank amount", bank_account_balance)
        # if bank_amount:
        amount = float(outstanding_pay_account_balance)
        print(amount)
        # else:
        #     amount = 0

        pay_id_list = []

        for k in self.invoice_line_ids:
            pay_id_list.append(k.id)

        if self.partner_type == 'customer':
            print("Customer Working", amount)
            transaction_line = [(0, 0, {
                'payment_ref': self.ref,
                'date': self.date,
                'partner_id': self.partner_id.id,
                'amount': self.amount,
            })]
            print("The amount should be ",float(amount) - self.amount)
            print("The amount should be ", self.amount)
            create_statement = self.env['account.bank.statement'].create({
                'journal_id': self.journal_id.id,
                'date': self.date,
                'company_id': self.company_id.id,
                'name': self.ref,
                'balance_start': float(amount)-self.amount,
                'balance_end_real': float(amount),
                'paid_amount': self.amount
                # 'line_ids': transaction_line,
            })

            if create_statement:
                create_statement.line_ids = transaction_line
                create_statement.move_line_ids = pay_id_list
                # create_statement.button_post()
                create_statement.write({'state': 'confirm'})


        if self.partner_type == 'supplier':
            print("Working", amount)
            transaction_line = [(0, 0, {
                'payment_ref': self.ref,
                'date': self.date,
                'partner_id': self.partner_id.id,
                'amount': -self.amount,
            })]

            create_statement = self.env['account.bank.statement'].create({
                'journal_id': self.journal_id.id,
                'date': self.date,
                'company_id': self.company_id.id,
                'name': self.ref,
                'balance_start': float(amount) + self.amount,
                'balance_end_real': float(amount),
                'paid_amount': -self.amount,
                # 'line_ids': transaction_line,
            })
            print("statement created", create_statement)
            if create_statement:
                create_statement.line_ids = transaction_line
                create_statement.move_line_ids = pay_id_list
                # create_statement.button_post()
                create_statement.write({'state': 'confirm'})

        return res_ids


class OpenAccountBalance(models.Model):
    _name = 'open.account.balance'

    create_date = fields.Date(string='Date')
    open_lines = fields.One2many('open.account.balance.line', 'open_id')
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('close', 'Closed'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3,
        default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'open.account.balance') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('open.account.balance') or _('New')
        return super(OpenAccountBalance, self).create(vals)

    def op_create(self):

        self.write({'state': 'close'})
        for line in self.open_lines:

            pay_id_list = []
            j = self.env['account.payment.method'].search([('name', '=', 'Manual')])[0]

            pay_id = self.env['account.payment'].create({'partner_id': line.journal_id.company_id.partner_id.id,
                                                         'amount': line.op_balance,
                                                         'partner_type': 'customer',
                                                         'payment_type': 'inbound',
                                                         'payment_method_id': j.id,
                                                         'journal_id': line.journal_id.id,
                                                         'ref': 'Opening Balance',
                                                         })
            pay_id.action_post()
            # for k in pay_id.invoice_line_ids:
            #     pay_id_list.append(k.id)
            #
            # stmt = self.env['account.bank.statement']
            # if not stmt:
            #     journ = line.journal_id
            #     # bal = sum(self.env['account.move.line'].search([('journal_id', '=', journ.id)]).mapped(
            #     #     'debit'))
            #     # journal_id = self.journal
            #     amount, nb_lines_bank_account_balance = journ._get_journal_bank_account_balance()
            #     if self.env['account.bank.statement'].search(
            #             [('company_id', '=', journ.company_id.id), ('journal_id', '=', journ.id)]):
            #         bal = amount
            #     else:
            #         bal = 0
            #         # self.env['account.bank.statement'].search(
            #         #     [('company_id', '=', journ.company_id.id), ('journal_id', '=', journ.id)])[
            #         #     0].balance_end_real
            #     stmt = self.env['account.bank.statement'].create(
            #         {'name': line.journal_id.company_id.partner_id.name,
            #          'balance_start': bal,
            #          # 'journal_id': line.journal_id.id,
            #          'journal_id': line.journal_id.id,
            #          'balance_end_real': bal + line.op_balance
            #
            #          })
            #     payment_list = []
            #     product_line = (0, 0, {
            #         'date': self.create_date,
            #         'payment_ref': 'Opening Balance',
            #         'name': self.name,
            #         'partner_id': line.journal_id.company_id.partner_id.id,
            #         'ref': self.name,
            #         'amount': line.op_balance
            #     })
            #
            #     payment_list.append(product_line)
            #
            # # move_id.action_cash_book()
            # if stmt:
            #     stmt.line_ids = payment_list
            #     stmt.move_line_ids = pay_id_list
            #     stmt.write({'state': 'confirm'})

            if line.account_id.name == 'Cash' and line.account_id.company_id.id == 1:
                j = line.journal_id
                # j = self.env['account.journal'].search(
                #     [('name', '=', 'Cash'), ('company_id', '=', self.env.user.company_id.id)])

                complete = sum(self.env['account.move.line'].search(
                    [('company_id', '=', self.env.user.company_id.id), ('account_id', '=', line.account_id.id)]).mapped(
                    'debit'))
                if not self.env['cash.book.info'].search([]):
                    amount, nb_lines_bank_account_balance = line.journal_id._get_journal_bank_account_balance()
                    if self.env['account.bank.statement'].search([('company_id', '=', line.journal_id.company_id.id),
                                                                  ('journal_id', '=', line.journal_id.id)]):
                        complete = int(amount)
                        print(amount)
                    else:
                        complete = 0

                    # complete = sum(
                    #     self.env['account.move.line'].search([('journal_id', '=', j.id)]).mapped('debit'))
                else:
                    complete = self.env['cash.book.info'].search([])[-1].balance + line.op_balance

                debit = 0
                credit = 0
                complete_new = 0
                type_m = 'inbound'
                label = 'Opening Balance' + '/' + line.account_id.name

                self.env['cash.book.info'].create({
                    'date': self.create_date,
                    'account_journal': j.id,
                    'account': line.account_id.id,
                    # 'partner_id': self.partner_id.id,
                    'company_id': self.env.user.company_id.id,
                    'description': label,
                    'payment_type': type_m,
                    # 'partner_type': self.partner_type,
                    'debit': line.op_balance,
                    'credit': 0,
                    # 'payment_id': self.id,
                    'balance': complete

                })

class OpenAccountBalanceLines(models.Model):
    _name = 'open.account.balance.line'

    open_id = fields.Many2one('open.account.balance')
    account_id = fields.Many2one('account.account', string='Account')
    journal_id = fields.Many2one('account.journal', string='Account')
    op_balance = fields.Float(string='Op Balance')

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            self.account_id = self.journal_id.payment_debit_account_id
