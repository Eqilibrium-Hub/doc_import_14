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



class CashBookInfo(models.Model):
    _name = "cash.book.info"
    _description = "Cash Report Line"

    date = fields.Date('Date')
    account = fields.Many2one('account.account')
    account_journal = fields.Many2one('account.journal')
    partner_id = fields.Many2one('res.partner', string='Partner')
    company_id = fields.Many2one('res.company', string='company')
    description = fields.Text(string='Description')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    balance = fields.Float('Balance')
    payment_id = fields.Many2one('account.payment')
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')])
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')], string='Payment Type')

