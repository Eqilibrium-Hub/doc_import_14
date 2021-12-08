from odoo import models,fields,api
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class SalesReport(models.Model):
    _name = 'sales.report'

    name = fields.Char(default='Sales Report',index=True)
    type = fields.Selection([('Day Book', 'Day Book'), ('Date Wise', 'Date Wise')], default='Day Book')
    from_date = fields.Date('From Date', default=datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    to_date = fields.Date('To Date', default=datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    date = fields.Date('Date', default=datetime.now().date().strftime(DEFAULT_SERVER_DATETIME_FORMAT))
    transaction_type = fields.Boolean(string='Transaction Type')
    transaction_type_sale = fields.Boolean(string='Sale',default=True)
    customer = fields.Many2one('res.partner')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    sales_report_lines=fields.One2many('sales.report.lines','sale_report_lines')


    @api.onchange('from_date','to_date','date','transaction_type_sale','customer')
    def create_sales_report_lines(self):
        if self.type == 'Day Book':
            if self.transaction_type_sale==True:
                self.sales_report_lines = None
                sale_report = self.env['account.payment'].search([('date', '=', self.date), ('payment_type', '=', 'inbound'),('partner_type', '=', 'customer')])
                sale_report_line = []
                for i in sale_report:
                    line_1 = (0, 0, {
                        'date': i.date,
                        'description': i.name,
                        'source': i.ref,
                        'customer': i.partner_id.name,
                        'invoice_amount': i.amount,
                        'debit': i.amount,
                        'credit': 0,
                    })
                    sale_report_line.append(line_1)
                self.update({
                    'sales_report_lines': sale_report_line
                })
                if self.customer:
                    self.sales_report_lines = None
                    sale_report = self.env['account.payment'].search([('date', '=', self.date), ('payment_type', '=', 'inbound'),('partner_type', '=', 'customer'),('partner_id','=',self.customer.name)])
                    sale_report_line = []
                    for i in sale_report:
                        line_1 = (0, 0, {
                            'date': i.date,
                            'description': i.name,
                            'source': i.ref,
                            'customer': i.partner_id.name,
                            'invoice_amount': i.amount,
                            'debit': i.amount,
                            'credit': 0,
                        })
                        sale_report_line.append(line_1)
                    self.update({
                        'sales_report_lines': sale_report_line
                    })
        if self.type == 'Date Wise':
            if self.from_date:
                if self.to_date:
                    if self.transaction_type_sale==True:
                        self.sales_report_lines = None
                        sale_report = self.env['account.payment'].search([('date', '>=', self.from_date),('date', '<=', self.to_date), ('payment_type', '=', 'inbound'),('partner_type', '=', 'customer')])
                        sale_report_line = []
                        for i in sale_report:
                            line_5 = (0, 0, {
                                'date': i.date,
                                'description': i.name,
                                'source': i.ref,
                                'customer': i.partner_id.name,
                                'invoice_amount': i.amount,
                                'debit': i.amount,
                                'credit': 0,
                            })
                            sale_report_line.append(line_5)
                        self.update({
                            'sales_report_lines': sale_report_line
                        })
                        if self.customer:
                            self.sales_report_lines = None
                            sale_report = self.env['account.payment'].search([('date', '>=', self.from_date), ('date', '<=', self.to_date),('payment_type', '=', 'inbound'),('partner_type', '=', 'customer'),('partner_id','=',self.customer.name)])
                            sale_report_line = []
                            for i in sale_report:
                                line_5 = (0, 0, {
                                    'date': i.date,
                                    'description': i.name,
                                    'source': i.ref,
                                    'customer': i.partner_id.name,
                                    'invoice_amount': i.amount,
                                    'debit': i.amount,
                                    'credit': 0,
                                })
                                sale_report_line.append(line_5)
                            self.update({
                                'sales_report_lines': sale_report_line
                            })


    # @api.multi
    def print_sales_report(self):
        return self.env.ref('advanced_common_day_book.sale_report_en_ar').report_action(self)


class SalesReportLines(models.Model):
    _name = 'sales.report.lines'

    sale_report_lines=fields.Many2one('sales.report')
    date = fields.Date('Date')
    description = fields.Char('Description')
    source = fields.Char('Source')
    customer = fields.Char('Customer')
    invoice_amount = fields.Float('Invoice Amount')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
