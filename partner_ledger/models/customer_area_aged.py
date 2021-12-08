# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import time
from datetime import datetime, timedelta
from odoo.tools.translate import _
import pytz
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dt
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class CustomerAgedReport(models.Model):
    _name = "customer.area.aged"
    _description = "Aged Report"
    _order = "id desc"

    name = fields.Char("Name", index=True, default=lambda self: _('New'))
    sequence = fields.Integer(index=True)

    state = fields.Selection([('draft', 'Draft'), ('validate', 'Done'), ('cancelled', 'Cancelled')], readonly=True,
                             default='draft', copy=False, string="Status")
    report_type = fields.Selection([('partner', 'Party Wise')],
                                   default='partner', copy=False, string="Report Type")

    partner_id = fields.Many2one('res.partner', string='Party Wise')
    summary_header = fields.Text("Summary Header")
    summary_footer = fields.Text("Summary Footer")
    room_summary = fields.Text("Building Summary")
    date_from = fields.Date("Date From")
    date_to = fields.Date("Date To")
    name = fields.Char("Name")

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        if self._context is None:
            self._context = {}
        res = super(CustomerAgedReport, self).default_get(fields)
        # Added default datetime as today and date to as today + 30.
        from_dt = datetime.today()
        dt_from = from_dt.strftime(dt)
        to_dt = from_dt + relativedelta(days=30)
        dt_to = to_dt.strftime(dt)
        # res.update({"from_date": dt_from, "to_date": dt_to})
        #
        # if not self.from_date and self.to_date:
        #     date_today = datetime.datetime.today()
        #     first_day = datetime.datetime(
        #         date_today.year, date_today.month, 1, 0, 0, 0
        #     )
        #     first_temp_day = first_day + relativedelta(months=1)
        #     last_temp_day = first_temp_day - relativedelta(days=1)
        #     last_day = datetime.datetime(
        #         last_temp_day.year,
        #         last_temp_day.month,
        #         last_temp_day.day,
        #         23,
        #         59,
        #         59,
        #     )
        #     date_froms = first_day.strftime(dt)
        #     date_ends = last_day.strftime(dt)
        res.update({})
        return res

    @api.onchange("report_type", "partner_id")
    def get_room_summary(self):
        # if self.from_date:
        #     self.to_date = self.from_date + relativedelta(months=1)
        """
        @param self: object pointer
         """
        res = {}
        all_detail = []
        room_obj = self.env["partner.ledger.customer"]
        reservation_line_obj = self.env["partner.ledger.customer"]
        folio_room_line_obj = self.env["partner.ledger.customer"]
        user_obj = self.env["res.users"]
        date_range_list = []
        main_header = []
        main_footer = []
        footer_details = []
        # footer_details.append('')
        # footer_details.append('Total')
        summary_header_list = ['SI.No']
        summary_header_list.append('Party Name')
        if self:
            temp_month = 1
            while temp_month <= 8:
                if temp_month == 1:
                    month_val = '<= 7'
                if temp_month == 2:
                    month_val = '<= 15'
                if temp_month == 3:
                    month_val = '<= 30'
                if temp_month == 4:
                    month_val = '<= 40'
                if temp_month == 5:
                    month_val = '<= 50'
                if temp_month == 6:
                    month_val = '<= 60'
                if temp_month == 7:
                    month_val = '<= 90'
                if temp_month == 8:
                    month_val = '>90'
                summary_header_list.append(month_val)
                date_range_list.append(month_val)
                temp_month += 1
                # # date_range_list(12)
                #
                # temp_date = temp_date + timedelta(days=1)

            summary_header_list.append('Total')
            room_ids = room_obj.search([])
            all_detail.append(summary_header_list)
            if self.report_type == 'partner':
                room_obj = self.env['account.move']
                room_ids = room_obj.search([('state', 'in', ('draft', 'open'))])
            all_room_detail = []
            if room_ids:
                amount = 0

                if self.report_type == 'partner':
                    room_detail = {}
                    if self.partner_id:
                        room_ids = room_ids.search(
                            [('partner_id', '=', self.partner_id.id), ('company_id', '=', self.env.user.company_id.id),
                             ('state', '=', 'open')])
                        k = 0
                        room_detail = {}
                        foot_detail = {}
                        room_list_stats = []

                        room_detail.update({"name": self.partner_id.name or ""})

                        i = 0
                        next_month = None
                        footer_details = []
                        for chk_date in date_range_list:
                            total_qty = 0
                            k = k + 1
                            room_detail.update({"sno": 1})
                            i = i + 1
                            qty = 0
                            total = 0
                            if i == 1:
                                first = datetime.today().date() + relativedelta(days=-7)
                                amount = round(sum(room_ids.search([('partner_id', '=', self.partner_id.id),
                                                                    ('company_id', '=', self.env.user.company_id.id),
                                                                    ('invoice_date', '>=', first),
                                                                    ('state', '=', 'open')]).mapped('amount_residual')))
                            elif i == 2:
                                first = datetime.today().date() + relativedelta(days=-8)
                                to = datetime.today().date() + relativedelta(days=-15)

                                amount = round(sum(room_ids.search([('partner_id', '=', self.partner_id.id),
                                                                    ('company_id', '=', self.env.user.company_id.id),
                                                                    ('invoice_date', '<=', first),
                                                                    ('invoice_date', '>=', to),
                                                                    ('state', '=', 'open')]).mapped('amount_residual')))

                            elif i == 3:
                                first = datetime.today().date() + relativedelta(days=-16)
                                to = datetime.today().date() + relativedelta(days=-30)

                                amount = round(sum(room_ids.search([('partner_id', '=', self.partner_id.id),
                                                                    ('company_id', '=', self.env.user.company_id.id),
                                                                    ('invoice_date', '<=', first),
                                                                    ('invoice_date', '>=', to),
                                                                    ('state', '=', 'open')]).mapped('amount_residual')))

                            elif i == 4:
                                first = datetime.today().date() + relativedelta(days=-31)
                                to = datetime.today().date() + relativedelta(days=-40)

                                amount = round(sum(room_ids.search([('partner_id', '=', self.partner_id.id),
                                                                    ('company_id', '=', self.env.user.company_id.id),
                                                                    ('invoice_date', '<=', first),
                                                                    ('invoice_date', '>=', to),
                                                                    ('state', '=', 'open')]).mapped('amount_residual')))
                            elif i == 5:
                                first = datetime.today().date() + relativedelta(days=-41)
                                to = datetime.today().date() + relativedelta(days=-50)

                                amount = round(sum(room_ids.search([('partner_id', '=', self.partner_id.id),
                                                                    ('company_id', '=', self.env.user.company_id.id),
                                                                    ('invoice_date', '<=', first),
                                                                    ('invoice_date', '>=', to),
                                                                    ('state', '=', 'open')]).mapped('amount_residual')))

                            elif i == 6:
                                first = datetime.today().date() + relativedelta(days=-51)
                                to = datetime.today().date() + relativedelta(days=-60)

                                amount = round(sum(room_ids.search([('partner_id', '=', self.partner_id.id),
                                                                    ('company_id', '=', self.env.user.company_id.id),
                                                                    ('invoice_date', '<=', first),
                                                                    ('invoice_date', '>=', to),
                                                                    ('state', '=', 'open')]).mapped('amount_residual')))

                            elif i == 7:
                                first = datetime.today().date() + relativedelta(days=-61)
                                to = datetime.today().date() + relativedelta(days=-90)

                                amount = round(sum(room_ids.search([('partner_id', '=', self.partner_id.id),
                                                                    ('company_id', '=', self.env.user.company_id.id),
                                                                    ('invoice_date', '<=', first),
                                                                    ('invoice_date', '>=', to),
                                                                    ('state', '=', 'open')]).mapped('amount_residual')))

                            elif i == 8:
                                first = datetime.today().date() + relativedelta(days=-91)
                                # to = datetime.today().date() + relativedelta(days=-51)

                                amount = round(sum(room_ids.search([('partner_id', '=', self.partner_id.id),
                                                                    ('company_id', '=', self.env.user.company_id.id),
                                                                    ('invoice_date', '<=', first),
                                                                    ('state', '=', 'open')]).mapped('amount_residual')))
                                amount += sum(self.env["partner.ledger.customer"].search(
                                    [('partner_id', '=', self.partner_id.id),
                                     ('company_id', '=', self.env.user.company_id.id)]).filtered(
                                    lambda a: a.description == 'Opening Balance').mapped('debit'))

                            room_list_stats.append(
                                {
                                    "state": "Free",
                                    # "date": chk_date,
                                    "room_id": self.partner_id.name,
                                    "qty": amount,
                                    "count": amount,

                                }
                            )

                            all_amount = round(
                                sum(room_ids.search([('partner_id', '=', self.partner_id.id), ('state', '=', 'open'),
                                                     ('company_id', '=', self.env.user.company_id.id), (
                                                         'invoice_date', '<=',
                                                         datetime.today().date())]).mapped('amount_residual')))
                            all_amount += sum(self.env["partner.ledger.customer"].search(
                                [('partner_id', '=', self.partner_id.id),
                                 ('company_id', '=', self.env.user.company_id.id)]).filtered(
                                lambda a: a.description == 'Opening Balance').mapped('debit'))

                            room_detail.update({"total": all_amount})
                            footer_details.append(str(amount))
                        room_detail.update({"value": room_list_stats})
                        all_room_detail.append(room_detail)
                        footer_details.append(str(all_amount))
            main_header.append({"header": summary_header_list})
            main_footer.append({"footer": footer_details})
            self.summary_header = str(main_header)
            self.summary_footer = str(main_footer)
            self.room_summary = str(all_room_detail)
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'customer.area.aged') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('customer.area.aged') or _('New')
        return super(CustomerAgedReport, self).create(vals)

