from odoo import models,fields,api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class CommonDayBook(models.Model):
    _name = 'common.day.book'

    name = fields.Char(default='Day Book',index=True)

    type=fields.Selection([('Day Book','Day Book'),('Date Wise','Date Wise')],default='Day Book')
    from_date=fields.Date('From Date',default=datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    to_date=fields.Date('To Date',default=datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    date=fields.Date('Date',default=datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    transaction_type=fields.Boolean(string='Transaction Type')
    transaction_type_sale=fields.Boolean(string='Sale')
    transaction_type_purchase=fields.Boolean(string='Purchase')
    transaction_type_expense=fields.Boolean(string='Expense')
    transaction_type_all=fields.Boolean(string='All',default=1)
    sale_check=fields.Char()
    pur_check=fields.Char()
    exp_check=fields.Char()
    all_check=fields.Char()
    company_id = fields.Many2one('res.company',string="company")
    common_day_book_lines=fields.One2many('common.day.book.lines','common_day_book_line')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)



    @api.onchange('transaction_type_sale','transaction_type_purchase','transaction_type_all')
    def onchange_values(self):
        if self.transaction_type_sale==True:
            self.sale_check='Sale'
        else:
            self.sale_check=False
        if self.transaction_type_purchase==True:
            self.pur_check = 'Purchase'
        else:
            self.pur_check = False
        if self.transaction_type_expense==True:
            self.exp_check='Expense'
        else:
            self.exp_check = False
        if self.transaction_type_all==True:
            self.all_check = 'All'
        else:
            self.all_check = False




    @api.onchange('date','type','transaction_type_sale','transaction_type_purchase','transaction_type_expense','transaction_type_all','from_date','to_date')
    def create_day_book_lines(self):
        if self.type == 'Day Book':
            if self.date:
                if self.transaction_type_all==True:
                    self.common_day_book_lines = None
                    day_book = self.env['account.payment'].search([('date', '=', self.date)])
                    book_lines = []
                    for i in day_book:
                        if i.partner_type == 'customer':
                            line = (0, 0, {
                                    'date': i.date,
                                    'description': i.name,
                                    'source': i.ref,
                                    'customer_name':i.partner_id.name,
                                    'invoice_amount':i.amount,
                                    'debit': i.amount,
                                    'credit': 0,
                            })
                            book_lines.append(line)
                        if i.partner_type == 'supplier':
                            line_a=(0, 0, {
                                    'date': i.date,
                                    'description': i.name,
                                    'source': i.ref,
                                     'customer_name': i.partner_id.name,
                                        'invoice_amount': i.amount,
                                        'debit': 0,
                                    'credit': i.amount,
                            })
                            book_lines.append(line_a)
                    self.update({
                        'common_day_book_lines': book_lines
                    })


                if self.transaction_type_sale==True:
                    self.common_day_book_lines = None
                    day_book=self.env['account.payment'].search([('date','=',self.date),('payment_type','=','inbound'),('partner_type','=','customer')])
                    book_lines_1=[]
                    for i in day_book:
                        line_1=(0, 0, {
                            'date':i.date,
                            'description':i.name,
                            'source':i.ref,
                            'customer_name': i.partner_id.name,
                            'invoice_amount': i.amount,
                            'debit':i.amount,
                            'credit':0,
                        })
                        book_lines_1.append(line_1)
                    self.update({
                        'common_day_book_lines':book_lines_1
                    })

                if self.transaction_type_purchase==True:
                    self.common_day_book_lines = None
                    day_book=self.env['account.payment'].search([('date','=',self.date),('payment_type','=', 'outbound'),('state', '=', 'posted'),('partner_type','=', 'supplier'),('expense_ref','=',False)])
                    # day_book=self.env['account.payment'].search([('date','=',self.date),('payment_type','=', 'outbound'),('partner_type','=', 'supplier')])
                    book_lines_2=[]
                    for i in day_book:
                        line_2=(0, 0, {
                            'date':i.date,
                            # 'description':'Local Purchase',
                            'description':i.name,
                            'source':i.ref,
                            'customer_name': i.partner_id.name,
                            'invoice_amount': i.amount,
                            'debit':0,
                            'credit':i.amount,
                        })
                        book_lines_2.append(line_2)
                    self.update({
                        'common_day_book_lines':book_lines_2
                    })

                if self.transaction_type_expense==True:
                    self.common_day_book_lines = None
                    day_book=self.env['hr.expense.sheet'].search([('accounting_date','=',self.date),('state','=', 'done')])
                    print(day_book,"day book")
                    book_lines_3=[]
                    for i in day_book:
                        line_3=(0, 0, {
                            'date':i.accounting_date,
                            'description':'Expense',
                            'source':i.name,
                            'customer_name': i.employee_id.name,
                            'invoice_amount': i.total_amount,
                            'debit':0,
                            'credit':i.total_amount,
                        })
                        book_lines_3.append(line_3)
                    self.update({
                        'common_day_book_lines':book_lines_3
                    })

        if self.type == 'Date Wise':
            if self.from_date:
                if self.to_date:
                    if self.transaction_type_all == True:
                        self.common_day_book_lines = None
                        day_book = self.env['account.payment'].search(
                            [('date', '>=', self.from_date), ('date', '<=', self.to_date)])
                        book_lines = []
                        for i in day_book:
                            if i.partner_type == 'customer':
                                line_4 = (0, 0, {
                                    'date': i.date,
                                    'description':i.name,
                                    'source': i.ref,
                                    'customer_name': i.partner_id.name,
                                    'invoice_amount': i.amount,
                                    'debit': i.amount,
                                    'credit': 0,
                                })
                                book_lines.append(line_4)
                            if i.partner_type == 'supplier':
                                line_4_a = (0, 0, {
                                    'date': i.date,
                                    'description': i.name,
                                    'source': i.ref,
                                    'customer_name': i.partner_id.name,
                                    'invoice_amount': i.amount,
                                    'debit': 0,
                                    'credit': i.amount,
                                })
                                book_lines.append(line_4_a)
                        self.update({
                            'common_day_book_lines': book_lines
                        })

                    if self.transaction_type_sale == True:
                        self.common_day_book_lines = None
                        day_book = self.env['account.payment'].search(
                            [('date', '>=', self.from_date),('date', '<=', self.to_date), ('payment_type', '=', 'inbound'),
                             ('partner_type', '=', 'customer')])
                        book_lines = []
                        for i in day_book:
                            line_5 = (0, 0, {
                                'date': i.date,
                                'description': i.name,
                                'source': i.ref,
                                'customer_name': i.partner_id.name,
                                'invoice_amount': i.amount,
                                'debit': i.amount,
                                'credit': 0,
                            })
                            book_lines.append(line_5)
                        self.update({
                            'common_day_book_lines': book_lines
                        })

                    if self.transaction_type_purchase==True:
                        self.common_day_book_lines = None
                        day_book = self.env['account.payment'].search([('date', '>=', self.from_date),('date', '<=', self.to_date), ('payment_type', '=', 'outbound'),('partner_type', '=', 'supplier'),('state','=','posted'),('expense_ref','=',False)])
                        book_lines = []
                        for i in day_book:
                            line_6 = (0, 0, {
                                'date': i.date,
                                'description': i.name,
                                'source': i.ref,
                                'customer_name': i.partner_id.name,
                                'invoice_amount': i.amount,
                                'debit': 0,
                                'credit': i.amount,
                            })
                            book_lines.append(line_6)
                        self.update({
                            'common_day_book_lines': book_lines
                        })

                    if self.transaction_type_expense==True:
                        self.common_day_book_lines = None
                        # day_book = self.env['account.payment'].search([('date', '>=', self.from_date),('date', '<=', self.to_date), ('state', '=', 'posted'),('expense_ref','!=',False)])
                        day_book = self.env['hr.expense.sheet'].search([('accounting_date', '>=', self.from_date),('accounting_date', '<=', self.to_date), ('state', '=', 'done')])
                        print(day_book,"date wise")
                        book_lines = []
                        for i in day_book:
                            line_7 = (0, 0, {
                                'date': i.accounting_date,
                                'description': 'Expense',
                                'source': i.name,
                                'customer_name': i.employee_id.name,
                                'invoice_amount': i.total_amount,
                                'debit': 0,
                                'credit': i.total_amount,
                            })
                            book_lines.append(line_7)
                        self.update({
                            'common_day_book_lines': book_lines
                        })

    # @api.multi
    def print_common_day_book(self):
        return self.env.ref('advanced_common_day_book.common_day_book_report_en_ar').report_action(self)


class DayBookLines(models.Model):
    _name = 'common.day.book.lines'

    common_day_book_line=fields.Many2one('common.day.book')
    date=fields.Date('Date')
    description=fields.Char('Description')
    source=fields.Char('Source')
    customer_name=fields.Char('Customer')
    invoice_amount = fields.Float('Invoice Amount')
    debit=fields.Float('Debit')
    credit=fields.Float('Credit')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

