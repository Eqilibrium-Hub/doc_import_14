from odoo import fields, models, api

class AccountingForm(models.Model):
    _name = 'accounting.form'


    date = fields.Date("Create Date")
    transfer = fields.One2many('bank.transfer', 'acc_id')
    reference = fields.Char("Reference")
    journal = fields.Many2one('account.journal',"Journal")
    service_state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ],
                                     string='Service Status', default='draft')
    type = fields.Selection([('expense','Expense'), ('journal', 'Journal')], default='expense')

    # @api.onchange('type')
    # def onchange_expense(self):


    def register_payment(self):
        val_list = []
        if self.type == 'expense':
            for line in self.transfer:
                if self.journal.type == 'cash' or self.journal.type == 'bank':
                    product_id = self.env['product.template'].search([('name', '=', 'Expenses')])
                    expense_id = self.env['hr.expense'].create({
                        # 'partner_type': 'supplier',
                        'product_id': product_id.id,
                        # 'destination_account_id': line.from_account.id,
                        'unit_amount': line.total_amount,
                        'name': self.reference,
                        # 'reference': self.reference,
                        'account_id': line.account.id,
                        # 'journal_id': self.journal.id

                    })
                    sheet = expense_id.action_submit_expenses()
                    invoices = self.env['hr.expense.sheet'].search([])[0]
                    print(invoices)
                    print(invoices)
                    invoices.action_submit_sheet()
                    invoices.approve_expense_sheets()
                    invoices.action_sheet_move_create()
                    moves = self.env['account.move'].search([])[0]
                    print(invoices.account_move_id)
                    pmt_wizard = self.env['account.payment.register'].with_context(active_model='account.move',
                                                                                   active_ids=invoices.account_move_id.ids).create({
                        'payment_date': self.date,
                        'journal_id': self.journal.id,
                        'amount': line.total_amount,
                        'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
                        # 'invoice_payments_widget':inv.amount_total

                    })
                    pmt_wizard._create_payments()
                    self.service_state = 'posted'

        if self.type == 'journal':
            for line in self.transfer:
                value = [(0, 0, {
                    'account_id': line.account.id,
                    'partner_id': line.partner.id,
                    'name': line.narration,
                    'debit': line.total_amount,
                    # 'credit': None
                })]

                value2 = [(0, 0, {
                    'account_id': line.from_account_first.id,
                    'partner_id': line.partner.id,
                    'name': line.narration,
                    # 'debit': None,
                    'credit': line.total_amount
                })]
                val_list = value + value2
                print(val_list)
            journal = self.env['account.move'].create({
                'ref': self.reference,
                'journal_id': self.journal.id,
                'line_ids': val_list
            })
            journal.action_post()
            # print(journal)
            # # self.env.ref('action_move_journal_line')
            self.service_state = 'posted'
            # #
            # #
            # print("Cash/ bank")
            # journal_id = self.journal
            # amount, nb_lines_bank_account_balance = journal_id._get_journal_bank_account_balance()
            # bank_amount = self.env['account.bank.statement'].search([('journal_id', '=', self.journal.id)])
            # if bank_amount:
            #     amount = int(amount)
            #     print("",amount)
            #
            # else:
            #     amount = 0
            #
            # pay_id_list = []
            #
            # for k in journal.invoice_line_ids:
            #     pay_id_list.append(k.id)
            # #     #
            # #     #
            # #     # transaction_line = [(0, 0, {
            # #     #     'payment_ref': journal.ref,
            # #     #     'date': journal.date,
            # #     #     'partner_id': journal.partner_id.id,
            # #     #     'amount': -journal.amount_total,
            # #     # })]
            # #     # create_statement = self.env['account.bank.statement'].create({
            # #     #     'journal_id': journal.journal_id.id,
            # #     #     'date': journal.date,
            # #     #     'company_id': journal.company_id.id,
            # #     #     'name': journal.ref,
            # #     #     'balance_start': int(amount),
            # #     #     'balance_end_real': int(amount) - journal.amount_total,
            # #     #     # 'line_ids': transaction_line,
            # #     # })
            # #     #
            # #     # if create_statement:
            # #     #     create_statement.line_ids = transaction_line
            # #     #     create_statement.move_line_ids = pay_id_list
            # #     #     create_statement.write({'state': 'confirm'})
            # #
            # #     # create_statement.button_post()
            # # #
            # if journal.partner_type == 'supplier':
            #     transaction_line = [(0, 0, {
            #         'payment_ref': journal.ref,
            #         'date': journal.date,
            #         'partner_id': journal.partner_id.id,
            #         'amount': -journal.amount,
            #     })]
            #     create_statement = self.env['account.bank.statement'].create({
            #         'journal_id': journal.journal_id.id,
            #         'date': journal.date,
            #         'company_id': journal.company_id.id,
            #         'name': journal.ref,
            #         'balance_start': int(amount),
            #         'balance_end_real': int(amount) - journal.amount,
            #         # 'line_ids': transaction_line,
            #     })
            #     print("statement created")
            #     if create_statement:
            #         create_statement.line_ids = transaction_line
            #         create_statement.move_line_ids = pay_id_list
            #         # create_statement.button_post()
            #         create_statement.write({'state': 'confirm'})



class BankTranfer(models.Model):
    _name = 'bank.transfer'

    acc_id = fields.Many2one('accounting.form')
    narration = fields.Char("Narration")
    from_acc_type = fields.Many2one('account.account.type', 'From Account Type')
    from_account_first = fields.Many2one('account.account', "From Account", domain="[('user_type_id', '=', from_acc_type)]")
    from_account = fields.Many2one('account.account', 'From', domain=lambda self: "[('user_type_id.type', '=', 'liquidity')]")
    acc_type = fields.Many2one('account.account.type', 'To Account Type', domain=lambda self: "[('name', '=', 'Expenses')]")
    # account = fields.Many2one('account.account',"Account", domain=lambda self: "[('user_type_id.type', '=', acc_type)]")
    account = fields.Many2one('account.account',"To Account", domain="[('user_type_id', '=', acc_type)]")
    partner = fields.Many2one('res.partner', "Partner")
    amount = fields.Float("Amount")
    # currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    total_amount = fields.Monetary('Transactions Subtotal', store=True, help="Total")
    #
    # loss_account_id = fields.Many2one(
    #     comodel_name='account.account', check_company=True,
    #     help="Used to register a loss when the ending balance of a cash register differs from what the system computes",
    #     string='Loss Account',
    #     domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
    #                              ('user_type_id.type', 'not in', ('receivable', 'payable')), \
    #                              ('user_type_id', '=', %s)]" % self.env.ref('account.data_account_type_expenses').id)
    currency_id = fields.Many2one('res.currency', string="Company Currency",
                                  default=lambda self: self.env.company.currency_id,
                                  store=True)



