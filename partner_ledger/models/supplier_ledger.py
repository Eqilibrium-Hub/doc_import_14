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


class SupplierLedgerCustom(models.Model):
    _name = 'supplier.ledger.customer'

    date = fields.Date('Date')
    paid_date = fields.Date('Paid Date')
    account = fields.Many2one('account.account')
    account_journal = fields.Many2one('account.journal')
    purchase_id = fields.Many2one('purchase.order', string="Purchase")
    invoice_id = fields.Many2one('account.move', string='BIll NO')
    account_move = fields.Many2one('account.move', string='Account Move')
    product_id = fields.Many2one('product.product', string='Product Name')
    partner_id = fields.Many2one('res.partner', string='Supplier')
    company_id = fields.Many2one('res.company', string='company')
    description = fields.Text(string='Description')
    uom = fields.Many2one('uom.uom', string='UoM')
    price_units = fields.Float('Unit')
    rate = fields.Float('Rate')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    balance = fields.Float('Balance')
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'),
                              ('10', 'October'), ('11', 'November'), ('12', 'December')])



