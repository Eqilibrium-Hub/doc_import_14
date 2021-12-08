from odoo import fields, models, api

class AccountingForm(models.Model):
    _name = 'account.form'

    date = fields.Date("Create Date")
    transfer = fields.One2many('bak.transfer', 'acc_id')
    reference = fields.Char("Reference")
    amount = fields.Float("Amount")
    journal = fields.Many2one('account.journal',"Journal")
    service_state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ],
                                     string='Service Status', default='draft')
    type = fields.Selection([('expense','Expense'), ('journal', 'Journal')], default='expense')
    type_payment = fields.Selection([('cash','cash'), ('bank', 'bank')],)

    @api.onchange('type_payment')
    # @api.depends('amount')
    def onchange_field(self):
        if self.type_payment == 'cash':
            account_id=self.env['account.journal'].search([('type','=','cash')])
            print(account_id)
            return{'domain':{'journal':[('id','in',account_id.ids)]}}
            # self.journal = account_id

        if not self.type_payment == 'cash':
            # self.type_payment== 'bank':
            acc_id=self.env['account.journal'].search([('type','=','bank')])
            return{'domain':{'journal':[('id','in',acc_id.ids)]}}

            # self.journal = acc_id



        # for line in self:
        #     for record in self.transfer:
        #         record.sgst = line.amount / 2.0
                # record.cgst = line.amount / 2.0
    @api.onchange('transfer')
    def dfg(self):
        for line in self:
            for record in self.transfer:
                record.sgst = line.amount / 2.0
                    # record.cgst = line.amount / 2.0

    # @api.onchange('amount')
    @api.onchange('transfer')
    # @api.depends('amount')
    def sfg(self):
        for line in self:
            for record in self.transfer:
                # record.sgst = line.amount / 2.0
                record.cgst = line.amount / 2.0






    def register_payment(self):
        val_list = []
        # accot_id=self.env['account.account'].search([('name','=','CGST Payable')])


        if self.type == 'expense':
            for line in self.transfer:
                value = (0, 0, {
                    'account_id': line.from_account.id,
                    # 'partner_id': line.partner.id,
                    # 'name': line.narration,
                    # 'debit': line.cgst,
                    'credit': self.amount,
                })
                val_list.append(value)


                # list = []
                for each_account in self.transfer.account:
                    value2 = (0, 0, {
                        'account_id': each_account.id,
                        # 'partner_id': line.partner.id,
                        # 'name': line.narration,
                        'debit': line.cgst,
                        # 'credit': line.sgst
                    })
                    val_list.append(value2)

            print(val_list)
            journal = self.env['account.move'].create({
                'ref': self.reference,
                'journal_id': self.journal.id,
                'line_ids': val_list

            })
            journal.action_post()
            print(journal)

            # journal_id = self.journal
            # amount, nb_lines_bank_account_balance = journal_id._get_journal_bank_account_balance()
            # pay_id_list = []
            #
            # for k in journal.invoice_line_ids:
            #     pay_id_list.append(k.id)
            #     print(pay_id_list)
            # journal.invoice_line_ids = pay_id_list
            # print(journal.invoice_line_ids)
            # bank_account_balance, nb_lines_bank_account_balance = journal_id._get_journal_bank_account_balance(
            #     domain=[('move_id.state', '=', 'posted')])
            # bank_amount = self.env['account.bank.statement'].search([('journal_id', '=', self.journal.id)])
            # # if bank_amount:
            # #     amount = float(bank_account_balance)
            # #     print(amount)
            # # else:
            # #     amount = 0
            #
            # pay_id_list = []
            #
            # for k in journal.invoice_line_ids:
            #     pay_id_list.append(k.id)
            #     print(pay_id_list)
            #
            # transaction_line = [(0, 0, {
            #     'payment_ref': journal.ref,
            #     'date': journal.date,
            #     'partner_id': journal.partner_id.id,
            #     'amount': -journal.amount_total,
            # })]
            # create_statement = self.env['account.bank.statement'].create({
            #     'journal_id': journal.journal_id.id,
            #     'date': journal.date,
            #     'company_id': journal.company_id.id,
            #     'name': journal.ref,
            #     'balance_start': float(amount) + float(journal.amount_total),
            #     'balance_end_real': float(amount),
            #     # 'line_ids': transaction_line,
            # })
            #
            # if create_statement:
            #     create_statement.line_ids = transaction_line
            #     # create_statement.move_line_ids = pay_id_list
            #     # create_statement.button_post()
            #     create_statement.write({'state': 'confirm'})




class BakTransfer(models.Model):
    _name = 'bak.transfer'




    def default_accounts(self):
        sgst = self.env['account.account'].search([('name','=','SGST Payable')])
        sgst += self.env['account.account'].search([('name','=','CGST Payable')])
        return sgst

    acc_id = fields.Many2one('account.form')
    sgst=fields.Float("SGST PAYABLE")
    cgst=fields.Float("CGST PAYABLE")
    label=fields.Char()
    acc_type = fields.Many2one('account.account.type', 'To Account Type')
    from_acc_type = fields.Many2one('account.account.type', 'From Account Type')

    from_account_first = fields.Many2one('account.account', "From Account", domain="[('user_type_id', '=', from_acc_type)]")


    from_account = fields.Many2one('account.account', 'From', domain=lambda self: "[('user_type_id.type', '=', 'liquidity')]")
    # to_account = fields.Many2one('account.account', 'To', domain="[('user_type_id.type', '=', 'other')]")
    account = fields.Many2many('account.account',default=default_accounts)
    # account = fields.Many2one('account.account',"To Account")
    # @api.onchange('from_account')
    # def sdfg(self):
    #     for record in self:
    #         record.cgst=record.cgst





    # narration = fields.Char("Narration")
    # from_acc_type = fields.Many2one('account.account.type', 'From Account Type')
    # from_account_first = fields.Many2one('account.account', "From Account", domain="[('user_type_id', '=', from_acc_type)]")
    # from_account = fields.Many2one('account.account', 'From', domain=lambda self: "[('user_type_id.type', '=', 'liquidity')]")
    # acc_type = fields.Many2one('account.account.type', 'To Account Type')
    # # account = fields.Many2one('account.account',"Account", domain=lambda self: "[('user_type_id.type', '=', acc_type)]")
    # account = fields.Many2one('account.account',"To Account", domain="[('user_type_id', '=', acc_type)]")
    # partner = fields.Many2one('res.partner', "Partner")
    # amount = fields.Float("Amount")
    # # currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    # total_amount = fields.Monetary('Transactions Subtotal', store=True, help="Total")
    # #
    # # loss_account_id = fields.Many2one(
    # #     comodel_name='account.account', check_company=True,
    # #     help="Used to register a loss when the ending balance of a cash register differs from what the system computes",
    # #     string='Loss Account',
    # #     domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
    # #                              ('user_type_id.type', 'not in', ('receivable', 'payable')), \
    # #                              ('user_type_id', '=', %s)]" % self.env.ref('account.data_account_type_expenses').id)
    # currency_id = fields.Many2one('res.currency', string="Company Currency",
    #                               default=lambda self: self.env.company.currency_id,
    #                               store=True)