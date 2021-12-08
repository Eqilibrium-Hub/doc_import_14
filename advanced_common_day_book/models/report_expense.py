from odoo import models,fields,api,_
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from werkzeug import url_encode


class account_payment(models.Model):
    _inherit = "account.payment"

    expense_ref = fields.Many2one('hr.expense.sheet')

class ReportExpense(models.Model):
    _name = 'report.expense'

    name = fields.Char(default='Expense Report',index=True)
    type = fields.Selection([('Day Book', 'Day Book'), ('Date Wise', 'Date Wise')], default='Day Book')
    from_date = fields.Date('From Date', default=datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    to_date = fields.Date('To Date', default=datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    date = fields.Date('Date', default=datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    transaction_type = fields.Boolean(string='Transaction Type')
    customer_employee = fields.Many2one('res.partner',string='Customer/Employee')
    transaction_type_expense=fields.Boolean(string='Expense',default=1)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    report_expense_lines = fields.One2many('report.expense.line','report_expenses')


    @api.onchange('from_date','to_date','date','transaction_type_expense','customer_employee')
    def create_report_expense_lines(self):
        if self.type == 'Day Book':
            if self.date:
                if self.transaction_type_expense==True:
                    self.report_expense_lines = None
                    # day_book=self.env['account.payment'].search([('payment_date','=',self.date),('payment_type','=', 'outbound'),('state', '=', 'posted'),('partner_type','=', 'supplier')])
                    # expense_report = self.env['account.payment'].search([('date', '=', self.date), ('payment_type', '=', 'outbound'),('state','=','reconciled'),('partner_type', '=', 'supplier')])
                    expense_report = self.env['hr.expense.sheet'].search([('accounting_date', '=', self.date),('state','=','done')])
                    book_lines_2 = []
                    for i in expense_report:
                        line_2 = (0, 0, {
                            'date': i.accounting_date,
                            # 'description':'Local Purchase',
                            'description': i.name,
                            'source': i.account_move_id.name,
                            'customer': i.employee_id.name,
                            'invoice_amount': i.total_amount,
                            'debit': 0,
                            'credit': i.total_amount,
                        })
                        book_lines_2.append(line_2)
                    self.update({
                        'report_expense_lines': book_lines_2
                    })
                    if self.customer_employee:
                        self.report_expense_lines = None
                        # day_book=self.env['account.payment'].search([('payment_date','=',self.date),('payment_type','=', 'outbound'),('state', '=', 'posted'),('partner_type','=', 'supplier')])
                        # expense_report = self.env['account.payment'].search([('date', '=', self.date), ('payment_type', '=', 'outbound'),('state', '=', 'reconciled'),('partner_type', '=', 'supplier')])
                        expense_report = self.env['hr.expense.sheet'].search([('accounting_date', '=', self.date),('state', '=', 'done'),('employee_id','=',self.customer_employee.name)])
                        book_lines_2 = []
                        for i in expense_report:
                            line_2 = (0, 0, {
                                'date': i.accounting_date,
                                # 'description':'Local Purchase',
                                'description': i.name,
                                'source': i.account_move_id.name,
                                'customer': i.employee_id.name,
                                'invoice_amount': i.total_amount,
                                'debit': 0,
                                'credit': i.total_amount,
                            })
                            book_lines_2.append(line_2)
                        self.update({
                            'report_expense_lines': book_lines_2
                        })
        if self.type == 'Date Wise':
            if self.from_date:
                if self.to_date:
                    if self.transaction_type_expense==True:
                        self.report_expense_lines = None
                        # expense_report = self.env['account.payment'].search([('date', '>=', self.from_date),('date', '<=', self.to_date), ('payment_type', '=', 'outbound'),('state','=','reconciled'),('partner_type', '=', 'supplier')])
                        expense_report = self.env['hr.expense.sheet'].search([('accounting_date', '>=', self.from_date),('accounting_date', '<=', self.to_date),('state','=','done')])
                        book_lines = []
                        for i in expense_report:
                            line_6 = (0, 0, {
                                'date': i.accounting_date,
                                'description': i.name,
                                'source': i.account_move_id.name,
                                'customer': i.employee_id.name,
                                'invoice_amount': i.total_amount,
                                'debit': 0,
                                'credit': i.total_amount,
                            })
                            book_lines.append(line_6)
                        self.update({
                            'report_expense_lines': book_lines
                        })
                        if self.customer_employee:
                            self.report_expense_lines = None
                            # expense_report = self.env['account.payment'].search([('date', '>=', self.from_date), ('date', '<=', self.to_date),('payment_type', '=', 'outbound'), ('state', '=', 'reconciled'),('partner_type', '=', 'supplier')])
                            expense_report = self.env['hr.expense.sheet'].search([('accounting_date', '>=', self.from_date), ('accounting_date', '<=', self.to_date), ('state', '=', 'done'),('employee_id','=',self.customer_employee.name)])
                            book_lines = []
                            for i in expense_report:
                                line_6 = (0, 0, {
                                    'date': i.accounting_date,
                                    'description': i.name,
                                    'source': i.account_move_id.name,
                                    'customer': i.employee_id.name,
                                    'invoice_amount': i.total_amount,
                                    'debit': 0,
                                    'credit': i.total_amount,
                                })
                                book_lines.append(line_6)
                            self.update({
                                'report_expense_lines': book_lines
                            })

    # @api.multi
    def print_expense_report(self):
        return self.env.ref('advanced_common_day_book.expense_report_en_ar').report_action(self)


class ReportExpenseLine(models.Model):
    _name = 'report.expense.line'

    report_expenses = fields.Many2one('report.expense')
    date = fields.Date('Date')
    description = fields.Char('Description')
    source = fields.Char('Source')
    customer = fields.Char('Customer/Employee')
    invoice_amount = fields.Float('Invoice Amount')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


# class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
#
#     _inherit = "hr.expense.sheet.register.payment.wizard"
#
#     expense_ref = fields.Many2one('hr.expense.sheet')
#
#     # @api.multi
#     def expense_post_payment(self):
#         self.ensure_one()
#         context = dict(self._context or {})
#         active_ids = context.get('active_ids', [])
#         expense_sheet = self.env['hr.expense.sheet'].browse(active_ids)
#
#         # Create payment and post it
#         payment = self.env['account.payment'].create(self._get_payment_vals())
#         payment.expense_ref = self.id
#         payment.post()
#
#         # Log the payment in the chatter
#         body = (_(
#             "A payment of %s %s with the reference <a href='/mail/view?%s'>%s</a> related to your expense %s has been made.") % (
#                 payment.amount, payment.currency_id.symbol,
#                 url_encode({'model': 'account.payment', 'res_id': payment.id}), payment.name, expense_sheet.name))
#         expense_sheet.message_post(body=body)
#
#         # Reconcile the payment and the expense, i.e. lookup on the payable account move lines
#         account_move_lines_to_reconcile = self.env['account.move.line']
#         for line in payment.move_line_ids + expense_sheet.account_move_id.line_ids:
#             if line.account_id.internal_type == 'payable' and not line.reconciled:
#                 account_move_lines_to_reconcile |= line
#         account_move_lines_to_reconcile.reconcile()
#
#         return {'type': 'ir.actions.act_window_close'}
