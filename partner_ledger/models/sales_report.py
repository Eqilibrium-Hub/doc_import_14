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



class SalesReportComp(models.Model):
    _name = "sale.report.custom"
    _description = "Sales Report"
    _order = "id desc"

    name = fields.Char("Name", index=True, default=lambda self: _('New'))
    sequence = fields.Integer(index=True)

    state = fields.Selection([('draft', 'Draft'), ('validate', 'Done'), ('cancelled', 'Cancelled')], readonly=True,
                             default='draft', copy=False, string="Status")
    payment_date = fields.Date(string='Create Date', default=fields.Date.context_today, required=True, copy=False)
    from_date = fields.Date(string='From Date', copy=False, default=fields.Date.context_today, )
    to_date = fields.Date(string='To Date', copy=False, default=fields.Date.context_today, )
    report_lines = fields.One2many('sale.report.custom.line', 'report_line')
    report_type = fields.Selection([ ('partner', 'Party Wise'),
                                    ('grouped', 'Product Group Wise'), ('product', 'Product Wise')],
                                   default='partner', copy=False, string="Report Type")
    product_type = fields.Selection(
        [('grouped', 'Product Group Wise'), ('product', 'Product Wise'), ('categ', 'Product Category')],
        copy=False, string="Product Filter")
    style = fields.Selection(
        [('normal', 'Normal'), ('summary', 'Summary'), ('monthly', 'Monthly')],
        default='normal', copy=False, string="Style")
    partner_id = fields.Many2one('res.partner', string='Party Wise')
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
                              ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'),
                              ('10', 'October'), ('11', 'November'), ('12', 'December')])

    product_group = fields.Many2one('product.template', domain=[('grouped', '=', True)])
    product_groups = fields.Many2one('product.template', domain=[('grouped', '=', True)])
    product_id = fields.Many2one('product.product', domain=[('grouped', '=', False), ('type', '=', 'product')])
    product_ids = fields.Many2one('product.product', domain=[('grouped', '=', False), ('type', '=', 'product')])
    product_categ = fields.Many2one('product.category', string='Product Category')
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
        res = super(SalesReportComp, self).default_get(fields)
        # Added default datetime as today and date to as today + 30.
        from_dt = datetime.today()
        dt_from = from_dt.strftime(dt)
        to_dt = from_dt + relativedelta(days=30)
        dt_to = to_dt.strftime(dt)
        # res.update({"from_date": dt_from, "to_date": dt_to})

        if not self.from_date and self.to_date:
            date_today = datetime.datetime.today()
            first_day = datetime.datetime(
                date_today.year, date_today.month, 1, 0, 0, 0
            )
            first_temp_day = first_day + relativedelta(months=1)
            last_temp_day = first_temp_day - relativedelta(days=1)
            last_day = datetime.datetime(
                last_temp_day.year,
                last_temp_day.month,
                last_temp_day.day,
                23,
                59,
                59,
            )
            date_froms = first_day.strftime(dt)
            date_ends = last_day.strftime(dt)
            res.update({"date_from": date_froms, "date_to": date_ends})
        return res

    @api.onchange("report_type", "product_id","product_group","partner_id","from_date","to_date")
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
        footer_details =[]
        # footer_details.append('')
        # footer_details.append('Total')
        summary_header_list = ['SI.No']
        summary_header_list.append('Party Name')
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise UserError(
                    _(
                        "Please Check Time period Date From can't \
                                   be greater than Date To !"
                    )
                )
            if self._context.get("tz", False):
                timezone = pytz.timezone(self._context.get("tz", False))
            else:
                timezone = pytz.timezone("UTC")
            d_frm_obj = (
                (self.from_date)
                    # .replace(tzinfo=pytz.timezone("UTC"))
                    # .astimezone(timezone)
            )
            d_to_obj = (
                (self.to_date)
                    # .replace(tzinfo=pytz.timezone("UTC"))
                    # .astimezone(timezone)
            )
            temp_date = d_frm_obj
            while temp_date <= d_to_obj:
                val = ""
                # val = (
                #         str(temp_date.strftime("%a"))
                #         + " "
                #         + str(temp_date.strftime("%b"))
                #         + " "
                #         + str(temp_date.strftime("%d"))
                # )
                date_range_list.append(temp_date.strftime(dt))
                val = (
                        str(temp_date.strftime("%a"))
                        + " "
                        + str(temp_date.strftime("%b"))
                        + " "
                        + str(temp_date.strftime("%d"))
                )
                summary_header_list.append(val+' '+'Qty')
                temp_date = temp_date + relativedelta(months=1)

            summary_header_list.append('Total Qty')
            all_detail.append(summary_header_list)
            room_ids = room_obj.search([('company_id','=',self.env.user.company_id.id),('month','>=',str(self.from_date.month))])
            all_room_detail = []
            if room_ids:
                if self.report_type not in ('product', 'grouped'):

                    if self.partner_id:
                        if room_ids.filtered(lambda a:a.partner_id == self.partner_id):
                            room_ids = room_ids.filtered(lambda a:a.partner_id == self.partner_id)[0]
                        else:
                            room_ids={}
                    k=0
                    total = 0
                    total_qty = 0

                    for room in room_ids:

                        k = k+1

                        room_detail = {}
                        foot_detail = {}
                        room_list_stats = []
                        room_detail.update({"sno": k})
                        room_detail.update({"name": room.partner_id.name or ""})
                        # if (
                        #         not room.room_reservation_line_ids
                        #         and not room.room_line_ids
                        # ):
                        i=0
                        next_month = None
                        footer_details = []
                        for chk_date in date_range_list:
                                total_qty = 0

                                i=i+1
                                qty=0

                                total=0
                                if not next_month:
                                   # last_month = self.from_date + relativedelta(months=-i)
                                   last_month = self.from_date

                                   if self.partner_id:
                                       # qty = sum(reservation_line_obj.search(
                                       #     [('company_id','=',self.env.user.company_id.id),('partner_id', '=', self.partner_id.id), ('date', '>=', last_month),
                                       #      ('date', '<=', chk_date)]).mapped('price_units'))
                                       qty = sum(reservation_line_obj.search(
                                           [('company_id','=',self.env.user.company_id.id),('partner_id', '=', self.partner_id.id),('month','=',str(last_month.month))]).mapped('price_units'))

                                       # total_qty = sum(reservation_line_obj.search(
                                       #     [('company_id','=',self.env.user.company_id.id),('partner_id', '=', self.partner_id.id), ('date', '>=', last_month),
                                       #      ('date', '<=', chk_date)]).mapped('price_units'))
                                       total_qty = sum(reservation_line_obj.search(
                                           [('company_id','=',self.env.user.company_id.id),('partner_id', '=', self.partner_id.id),('month','=',str(last_month.month))]).mapped('price_units'))
                                       # footer_details.update({total_qty})
                                       # footer_details.append(str(total_qty))

                                       # total = sum(reservation_line_obj.search(
                                       #     [('company_id','=',self.env.user.company_id.id),('partner_id', '=', self.partner_id.id), ('date', '>=', last_month),
                                       #      ('date', '<=', self.to_date)]).mapped('price_units'))
                                       total = sum(reservation_line_obj.search(
                                           [('company_id','=',self.env.user.company_id.id),('partner_id', '=', self.partner_id.id), ('month','>=',str(last_month.month)),
                                            ('month', '<=', str(self.to_date.month))]).mapped('price_units'))
                                       room_detail.update({"total": total})
                                   else:

                                       # total = sum(reservation_line_obj.search(
                                       #     [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('date', '>=', self.from_date),
                                       #      ('date', '<=', self.to_date)]).mapped('price_units'))
                                       total = sum(reservation_line_obj.search(
                                           [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('month', '>=', str(self.from_date.month)),
                                            ('month', '<=', str(self.to_date.month))]).mapped('price_units'))
                                       # qty = sum(reservation_line_obj.search(
                                       #     [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('date', '>=', self.from_date),
                                       #      ('date', '<=',chk_date)]).mapped('price_units'))
                                       qty = sum(reservation_line_obj.search(
                                           [('company_id','=',self.env.user.company_id.id),('id', '=', room.id),('month','=',str(last_month.month))]).mapped('price_units'))


                                       room_detail.update({"total": total})
                                       total_qty = sum(reservation_line_obj.search(
                                           [('company_id','=',self.env.user.company_id.id),('month','=',str(last_month.month))]).mapped('price_units'))

                                   next_month = last_month + relativedelta(months=i)
                                else:
                                    if self.partner_id:
                                        # qty = sum(reservation_line_obj.search([('company_id','=',self.env.user.company_id.id),('partner_id','=',self.partner_id.id),('date','>=', next_month),('date','<=',chk_date)]).mapped('price_units'))
                                        qty = sum(reservation_line_obj.search([('company_id','=',self.env.user.company_id.id),('partner_id','=',self.partner_id.id),('month','=',str(next_month.month))]).mapped('price_units'))
                                        # total = sum(reservation_line_obj.search([('company_id','=',self.env.user.company_id.id),('partner_id','=',self.partner_id.id),('date','>=', self.from_date),('date','<=',self.to_date)]).mapped('price_units'))
                                        total = sum(reservation_line_obj.search([('company_id','=',self.env.user.company_id.id),('partner_id','=',self.partner_id.id),('month','>=', str(self.from_date.month)),('month','<=',str(self.to_date.month))]).mapped('price_units'))
                                        room_detail.update({"total": total})
                                        # total_qty = sum(reservation_line_obj.search(
                                        #     [('company_id','=',self.env.user.company_id.id),('partner_id', '=', self.partner_id.id), ('date', '>=', next_month),
                                        #      ('date', '<=', chk_date)]).mapped('price_units'))
                                        total_qty = sum(reservation_line_obj.search(
                                            [('company_id','=',self.env.user.company_id.id),('partner_id', '=', self.partner_id.id),('month','=',str(next_month.month))]).mapped('price_units'))
                                    else:
                                        # total = sum(reservation_line_obj.search([('company_id','=',self.env.user.company_id.id),('id','=',room.id),('date','>=', self.from_date),('date','<=',self.to_date)]).mapped('price_units'))
                                        total = sum(reservation_line_obj.search([('company_id','=',self.env.user.company_id.id),('id','=',room.id),('month','>=', str(self.from_date.month)),('month','<=',str(self.to_date.month))]).mapped('price_units'))
                                        # qty = sum(reservation_line_obj.search([('company_id','=',self.env.user.company_id.id),('id','=',room.id),('date','>=', next_month),('date','<=',chk_date)]).mapped('price_units'))
                                        qty = sum(reservation_line_obj.search([('company_id','=',self.env.user.company_id.id),('id','=',room.id),('month','=',str(next_month.month))]).mapped('price_units'))
                                        room_detail.update({"total": total})
                                        # total_qty = sum(reservation_line_obj.search(
                                        #     [('company_id','=',self.env.user.company_id.id),('date', '>=', next_month),
                                        #      ('date', '<=', chk_date)]).mapped('price_units'))
                                        total_qty = sum(reservation_line_obj.search(
                                            [('company_id','=',self.env.user.company_id.id),('month','=',str(next_month.month))]).mapped('price_units'))

                                    next_month = last_month+ relativedelta(months=i)
                                room_list_stats.append(
                                    {
                                        "state": "Free",
                                        "date": chk_date,
                                        "room_id": room.product_id.name,
                                        "qty": qty,
                                        "count": total,


                                    }
                                )
                                footer_details.append(str(total_qty))
                        print(room_detail)
                        room_detail.update({"value": room_list_stats})
                        all_room_detail.append(room_detail)

                    if not self.partner_id:
                        total_qty = sum(reservation_line_obj.search(
                            [('company_id','=',self.env.user.company_id.id),('month', '>=', str(self.from_date.month)),
                             ('month', '<=', str(self.to_date.month))]).mapped('price_units'))
                        # total_qty = sum(reservation_line_obj.search(
                        #     [('company_id','=',self.env.user.company_id.id),('month','=',str(next_month.month))]).mapped('price_units'))
                        footer_details.append(str(total_qty))
                    else:
                        footer_details.append(str(total))

                    main_header.append({"header": summary_header_list})
                    main_footer.append({"footer": footer_details})
                    self.summary_header = str(main_header)
                    self.summary_footer = str(main_footer)
                    self.room_summary = str(all_room_detail)
                if self.report_type == 'product':

                    summary_header_list.pop(1)
                    summary_header_list.insert(1,'Product Name')

                    if self.product_id:
                        if room_ids.filtered(lambda a: a.product_id == self.product_id):
                           room_ids = room_ids.filtered(lambda a: a.product_id == self.product_id)[0]
                        else:
                            room_ids ={}

                    k = 0
                    total = 0
                    total_qty = 0


                    for room in room_ids:

                        k = k + 1

                        room_detail = {}
                        foot_detail = {}
                        room_list_stats = []
                        room_detail.update({"sno": k})
                        room_detail.update({"name": room.product_id.name})
                        # if (
                        #         not room.room_reservation_line_ids
                        #         and not room.room_line_ids
                        # ):
                        i = 0
                        next_month = None
                        footer_details = []
                        for chk_date in date_range_list:
                            total_qty = 0

                            i = i + 1
                            qty = 0

                            total = 0
                            if not next_month:
                                # last_month = self.from_date + relativedelta(months=-i)
                                last_month = self.from_date

                                if self.product_id:
                                    # qty = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id), ('date', '>=', last_month),
                                    #      ('date', '<=', chk_date)]).mapped('price_units'))
                                    qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id),('month','=',str(last_month.month))]).mapped('price_units'))

                                    # total_qty = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id), ('date', '>=', last_month),
                                    #      ('date', '<=', chk_date)]).mapped('price_units'))
                                    total_qty = sum(reservation_line_obj.search(
                                    [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id),('month','=',str(last_month.month))]).mapped('price_units'))
                                # footer_details.update({total_qty})
                                    # footer_details.append(str(total_qty))

                                    # total = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id), ('date', '>=', last_month),
                                    #      ('date', '<=', self.to_date)]).mapped('price_units'))
                                    total = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id), ('month', '>=', str(last_month.month)),
                                         ('month', '<=', str(self.to_date.month))]).mapped('price_units'))
                                    room_detail.update({"total": total})
                                else:

                                    # total = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('date', '>=', self.from_date),
                                    #      ('date', '<=', self.to_date)]).mapped('price_units'))
                                    total = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('month', '>=', str(self.from_date.month)),
                                         ('month', '<=', str(self.to_date.month))]).mapped('price_units'))
                                    # qty = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('date', '>=', self.from_date),
                                    #      ('date', '<=', chk_date)]).mapped('price_units'))
                                    qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('id', '=', room.id),('month','=',str(last_month.month))]).mapped('price_units'))
                                    room_detail.update({"total": total})
                                    # total_qty = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('date', '>=', self.from_date),
                                    #      ('date', '<=', chk_date)]).mapped('price_units'))
                                    total_qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('month','=',str(last_month.month))]).mapped('price_units'))

                                next_month = last_month + relativedelta(months=i)
                            else:
                                if self.product_id:
                                    # qty = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id), ('date', '>=', next_month),
                                    #      ('date', '<=', chk_date)]).mapped('price_units'))
                                    qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id),('month','=',str(next_month.month))]).mapped('price_units'))
                                    # total = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id), ('date', '>=', self.from_date),
                                    #      ('date', '<=', self.to_date)]).mapped('price_units'))
                                    total = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id), ('month', '>=', str(self.from_date.month)),
                                         ('month', '<=', str(self.to_date.month))]).mapped('price_units'))
                                    room_detail.update({"total": total})
                                    # total_qty = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id), ('date', '>=', next_month),
                                    #      ('date', '<=', chk_date)]).mapped('price_units'))
                                    total_qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('product_id', '=', self.product_id.id),('month','=',str(next_month.month))]).mapped('price_units'))
                                else:
                                    # total = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('date', '>=', self.from_date),
                                    #      ('date', '<=', chk_date)]).mapped('price_units'))
                                    total = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('month', '>=', str(self.from_date.month)),
                                         ('month','=',str(next_month.month))]).mapped('price_units'))
                                    # qty = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('date', '>=', next_month),
                                    #      ('date', '<=', chk_date)]).mapped('price_units'))
                                    qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('id', '=', room.id),('month','=',str(next_month.month))]).mapped('price_units'))
                                    room_detail.update({"total": total})
                                    # total_qty = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('date', '>=', next_month),
                                    #      ('date', '<=', chk_date)]).mapped('price_units'))
                                    total_qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('month','=',str(next_month.month))]).mapped('price_units'))
                                next_month = last_month + relativedelta(months=i)
                            room_list_stats.append(
                                {
                                    "state": "Free",
                                    "date": chk_date,
                                    "room_id": room.product_id.name,
                                    "qty": qty,
                                    "count": total,

                                }
                            )
                            footer_details.append(str(total_qty))
                        print(room_detail)
                        room_detail.update({"value": room_list_stats})
                        all_room_detail.append(room_detail)

                    if not self.product_id:
                        total_qty = sum(reservation_line_obj.search(
                            [('company_id','=',self.env.user.company_id.id),('month', '>=', str(self.from_date.month)),
                             ('month', '<=', str(self.to_date.month))]).mapped('price_units'))
                        footer_details.append(str(total_qty))
                    else:
                        footer_details.append(str(total))

                    main_header.append({"header": summary_header_list})
                    main_footer.append({"footer": footer_details})
                    self.summary_header = str(main_header)
                    self.summary_footer = str(main_footer)
                    self.room_summary = str(all_room_detail)
                if self.report_type == 'grouped':

                    summary_header_list.pop(1)
                    summary_header_list.insert(1,'Group Name')

                    if self.product_group:
                        # if each_coll.product_id.parent_id == self.product_groups:
                        if room_ids.filtered(lambda a: a.product_id.parent_id == self.product_group):
                            room_ids = room_ids.filtered(lambda a: a.product_id.parent_id == self.product_group)[0]
                        else:
                            room_ids = {}
                    k = 0
                    total = 0
                    total_qty = 0

                    for room in room_ids:

                        k = k + 1

                        room_detail = {}
                        foot_detail = {}
                        room_list_stats = []
                        room_detail.update({"sno": k})
                        if self.product_group:
                            room_detail.update({"name": self.product_group.name})
                        else:
                            room_detail.update({"name": room.product_id.parent_id.name})
                        # if (
                        #         not room.room_reservation_line_ids
                        #         and not room.room_line_ids
                        # ):
                        i = 0
                        next_month = None
                        footer_details = []
                        for chk_date in date_range_list:
                            total_qty = 0

                            i = i + 1
                            qty = 0

                            total = 0
                            if not next_month:
                                # last_month = self.from_date + relativedelta(months=-i)
                                last_month = self.from_date

                                if self.product_group:
                                    qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('month','=',str(last_month.month))]).filtered(lambda a: a.product_id.parent_id == self.product_group).mapped('price_units'))

                                    total_qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('month','=',str(last_month.month))]).filtered(lambda a: a.product_id.parent_id == self.product_group).mapped('price_units'))

                                    total = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('month', '>=', str(last_month.month)),
                                         ('month', '<=', str(self.to_date.month))]).filtered(lambda a: a.product_id.parent_id == self.product_group).mapped('price_units'))
                                    room_detail.update({"total": total})
                                else:
                                    #
                                    # total = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('date', '>=', self.from_date),
                                    #      ('date', '<=', self.to_date)]).mapped('price_units'))
                                    total = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('month', '>=', str(self.from_date.month)),
                                         ('month', '<=', str(self.to_date.month))]).mapped('price_units'))
                                    # qty = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('date', '>=', self.from_date),
                                    #      ('date', '<=', chk_date)]).mapped('price_units'))
                                    qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('id', '=', room.id),('month','=',str(last_month.month))]).mapped('price_units'))
                                    room_detail.update({"total": total})
                                    total_qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('month','=',str(last_month.month))]).mapped('price_units'))

                                next_month = last_month+ relativedelta(months=i)
                            else:
                                if self.product_group:
                                    qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('month','=',str(next_month.month))]).filtered(lambda a: a.product_id.parent_id == self.product_group).mapped('price_units'))
                                    total = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('month', '>=', str(self.from_date.month)),
                                         ('month', '<=', str(self.to_date.month))]).filtered(lambda a: a.product_id.parent_id == self.product_group).mapped('price_units'))
                                    room_detail.update({"total": total})
                                    # total_qty = sum(reservation_line_obj.search(
                                    #     [('company_id','=',self.env.user.company_id.id),('date', '>=', next_month),
                                    #      ('date', '<=', chk_date)]).filtered(lambda a: a.product_id.parent_id == self.product_group).mapped('price_units'))
                                    total_qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('month','=',str(next_month.month))]).filtered(lambda a: a.product_id.parent_id == self.product_group).mapped('price_units'))
                                else:
                                    total = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('id', '=', room.id), ('month', '>=', str(self.from_date.month)),
                                         ('month', '<=', str(self.to_date.month))]).mapped('price_units'))
                                    qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('id', '=', room.id),('month','=',str(next_month.month))]).mapped('price_units'))
                                    room_detail.update({"total": total})
                                    total_qty = sum(reservation_line_obj.search(
                                        [('company_id','=',self.env.user.company_id.id),('month','=',str(next_month.month))]).mapped('price_units'))
                                next_month = last_month + relativedelta(months=i)
                            room_list_stats.append(
                                {
                                    "state": "Free",
                                    "date": chk_date,
                                    "room_id": room.product_id.name,
                                    "qty": qty,
                                    "count": total,

                                }
                            )
                            footer_details.append(str(total_qty))
                        print(room_detail)
                        room_detail.update({"value": room_list_stats})
                        all_room_detail.append(room_detail)

                    if not self.product_group:
                        total_qty = sum(reservation_line_obj.search(
                            [('company_id','=',self.env.user.company_id.id),('month', '>=', str(self.from_date.month)),
                             ('month', '<=', str(self.to_date.month))]).mapped('price_units'))
                        footer_details.append(str(total_qty))
                    else:
                        footer_details.append(str(total))

                    main_header.append({"header": summary_header_list})
                    main_footer.append({"footer": footer_details})
                    self.summary_header = str(main_header)
                    self.summary_footer = str(main_footer)
                    self.room_summary = str(all_room_detail)
            else:
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
                    'sale.report.custom') or _('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.report.custom') or _('New')
        return super(SalesReportComp, self).create(vals)

    @api.onchange('from_date', 'product_categ', 'product_groups', 'product_ids', 'product_type', 'style', 'month',
                  'product_group', 'product_id', 'to_date', 'report_type', 'partner_id')
    def onchange_form_date(self):
        if self.style != 'monthly':

            self.report_lines = False
            if self.report_type == 'partner':
                self.report_lines = False
                if self.partner_id:
                    if self.product_groups and not self.product_ids and not self.product_categ:
                        today_total_cheques = []
                        for each_coll in self.env['partner.ledger.customer'].search(
                                [('company_id', '=', self.env.user.company_id.id), ('partner_id', '=', self.partner_id.id),
                                 ('date', '>=', self.from_date),
                                 ('date', '<=', self.to_date),('product_id','!=',False)]):
                            if each_coll.product_id.parent_id == self.product_groups:
                                product_line = (0, 0, {
                                    'date': each_coll.date,
                                    'invoice_id': each_coll.invoice_id.id,
                                    'partner_id': each_coll.partner_id.id,
                                    'product_id': each_coll.product_id.id,
                                    'company_id': each_coll.company_id.id,
                                    'price_units': each_coll.price_units,
                                    'uom': each_coll.uom.id,
                                    'rate': each_coll.rate,
                                    'credit': each_coll.credit,
                                    'debit': each_coll.debit,
                                    'description': each_coll.description,
                                    'account_journal': each_coll.account_journal.id,
                                    'account': each_coll.account.id,
                                    'paid_date': each_coll.paid_date

                                })
                                today_total_cheques.append(product_line)
                    elif self.product_ids and not self.product_categ and not self.product_groups:
                        today_total_cheques = []
                        for each_coll in self.env['partner.ledger.customer'].search(
                                [('product_id', '=', self.product_ids.id), ('company_id', '=', self.env.user.company_id.id),
                                 ('partner_id', '=', self.partner_id.id), ('date', '>=', self.from_date),
                                 ('date', '<=', self.to_date)]):
                            product_line = (0, 0, {
                                'date': each_coll.date,
                                'invoice_id': each_coll.invoice_id.id,
                                'partner_id': each_coll.partner_id.id,
                                'product_id': each_coll.product_id.id,
                                'company_id': each_coll.company_id.id,
                                'price_units': each_coll.price_units,
                                'uom': each_coll.uom.id,
                                'rate': each_coll.rate,
                                'credit': each_coll.credit,
                                'debit': each_coll.debit,
                                'description': each_coll.description,
                                'account_journal': each_coll.account_journal.id,
                                'account': each_coll.account.id,
                                'paid_date': each_coll.paid_date

                            })
                            today_total_cheques.append(product_line)
                    elif self.product_categ and not self.product_ids and not self.product_groups:
                        today_total_cheques = []
                        for each_coll in self.env['partner.ledger.customer'].search(
                                [('company_id', '=', self.env.user.company_id.id),('product_id','!=',False),('partner_id', '=', self.partner_id.id),
                                 ('date', '>=', self.from_date),
                                 ('date', '<=', self.to_date)]):
                            if each_coll.product_id.categ_id == self.product_categ:
                                product_line = (0, 0, {
                                    'date': each_coll.date,
                                    'invoice_id': each_coll.invoice_id.id,
                                    'partner_id': each_coll.partner_id.id,
                                    'product_id': each_coll.product_id.id,
                                    'company_id': each_coll.company_id.id,
                                    'price_units': each_coll.price_units,
                                    'uom': each_coll.uom.id,
                                    'rate': each_coll.rate,
                                    'credit': each_coll.credit,
                                    'debit': each_coll.debit,
                                    'description': each_coll.description,
                                    'account_journal': each_coll.account_journal.id,
                                    'account': each_coll.account.id,
                                    'paid_date': each_coll.paid_date

                                })
                                today_total_cheques.append(product_line)
                    elif self.product_groups and self.product_categ and not self.product_ids:
                        today_total_cheques = []
                        for each_coll in self.env['partner.ledger.customer'].search(
                                [('company_id', '=', self.env.user.company_id.id), ('product_id','!=',False),('partner_id', '=', self.partner_id.id),
                                 ('date', '>=', self.from_date),
                                 ('date', '<=', self.to_date)]):
                            if each_coll.product_id.parent_id == self.product_groups:
                                if each_coll.product_id.categ_id == self.product_categ:
                                    product_line = (0, 0, {
                                        'date': each_coll.date,
                                        'invoice_id': each_coll.invoice_id.id,
                                        'partner_id': each_coll.partner_id.id,
                                        'product_id': each_coll.product_id.id,
                                        'company_id': each_coll.company_id.id,
                                        'price_units': each_coll.price_units,
                                        'uom': each_coll.uom.id,
                                        'rate': each_coll.rate,
                                        'credit': each_coll.credit,
                                        'debit': each_coll.debit,
                                        'description': each_coll.description,
                                        'account_journal': each_coll.account_journal.id,
                                        'account': each_coll.account.id,
                                        'paid_date': each_coll.paid_date

                                    })
                                    today_total_cheques.append(product_line)
                    elif self.product_groups and self.product_categ and self.product_ids:
                        today_total_cheques = []
                        for each_coll in self.env['partner.ledger.customer'].search(
                                [('product_id', '=', self.product_ids.id), ('company_id', '=', self.env.user.company_id.id),
                                 ('partner_id', '=', self.partner_id.id), ('date', '>=', self.from_date),
                                 ('date', '<=', self.to_date)]):
                            if each_coll.product_id.parent_id == self.product_groups:
                                if each_coll.product_id.categ_id == self.product_categ:
                                    product_line = (0, 0, {
                                        'date': each_coll.date,
                                        'invoice_id': each_coll.invoice_id.id,
                                        'partner_id': each_coll.partner_id.id,
                                        'product_id': each_coll.product_id.id,
                                        'company_id': each_coll.company_id.id,
                                        'price_units': each_coll.price_units,
                                        'uom': each_coll.uom.id,
                                        'rate': each_coll.rate,
                                        'credit': each_coll.credit,
                                        'debit': each_coll.debit,
                                        'description': each_coll.description,
                                        'account_journal': each_coll.account_journal.id,
                                        'account': each_coll.account.id,
                                        'paid_date': each_coll.paid_date

                                    })
                                    today_total_cheques.append(product_line)
                    elif self.product_groups and not self.product_categ and self.product_ids:
                        today_total_cheques = []
                        for each_coll in self.env['partner.ledger.customer'].search(
                                [('product_id', '=', self.product_ids.id), ('company_id', '=', self.env.user.company_id.id),
                                 ('partner_id', '=', self.partner_id.id), ('date', '>=', self.from_date),
                                 ('date', '<=', self.to_date)]):
                            if each_coll.product_id.parent_id == self.product_groups:
                                product_line = (0, 0, {
                                    'date': each_coll.date,
                                    'invoice_id': each_coll.invoice_id.id,
                                    'partner_id': each_coll.partner_id.id,
                                    'product_id': each_coll.product_id.id,
                                    'company_id': each_coll.company_id.id,
                                    'price_units': each_coll.price_units,
                                    'uom': each_coll.uom.id,
                                    'rate': each_coll.rate,
                                    'credit': each_coll.credit,
                                    'debit': each_coll.debit,
                                    'description': each_coll.description,
                                    'account_journal': each_coll.account_journal.id,
                                    'account': each_coll.account.id,
                                    'paid_date': each_coll.paid_date

                                })
                                today_total_cheques.append(product_line)



                    else:
                        today_total_cheques = []
                        for each_coll in self.env['partner.ledger.customer'].search(
                                [('company_id', '=', self.env.user.company_id.id), ('product_id','!=',False),('partner_id', '=', self.partner_id.id),
                                 ('date', '>=', self.from_date),
                                 ('date', '<=', self.to_date)]):
                            product_line = (0, 0, {
                                'date': each_coll.date,
                                'invoice_id': each_coll.invoice_id.id,
                                'partner_id': each_coll.partner_id.id,
                                'product_id': each_coll.product_id.id,
                                'company_id': each_coll.company_id.id,
                                'price_units': each_coll.price_units,
                                'uom': each_coll.uom.id,
                                'rate': each_coll.rate,
                                'credit': each_coll.credit,
                                'debit': each_coll.debit,
                                'description': each_coll.description,
                                'account_journal': each_coll.account_journal.id,
                                'account': each_coll.account.id,
                                'paid_date': each_coll.paid_date

                            })
                            today_total_cheques.append(product_line)
                else:
                    today_total_cheques = []
                    for each_coll in self.env['partner.ledger.customer'].search(
                            [('company_id', '=', self.env.user.company_id.id),('product_id','!=',False),('date', '>=', self.from_date),
                             ('date', '<=', self.to_date)]):
                        product_line = (0, 0, {
                            'date': each_coll.date,
                            'invoice_id': each_coll.invoice_id.id,
                            'partner_id': each_coll.partner_id.id,
                            'product_id': each_coll.product_id.id,
                            'company_id': each_coll.company_id.id,
                            'price_units': each_coll.price_units,
                            'uom': each_coll.uom.id,
                            'rate': each_coll.rate,
                            'credit': each_coll.credit,
                            'debit': each_coll.debit,
                            'description': each_coll.description,
                            'account_journal': each_coll.account_journal.id,
                            'account': each_coll.account.id,
                            'paid_date': each_coll.paid_date

                        })
                        today_total_cheques.append(product_line)
                self.report_lines = today_total_cheques
            if self.report_type == 'product':
                self.report_lines = False
                if self.product_id:
                    today_total_cheques = []
                    for each_coll in self.env['partner.ledger.customer'].search(
                            [('company_id', '=', self.env.user.company_id.id), ('product_id', '=', self.product_id.id),
                             ('date', '>=', self.from_date),
                             ('date', '<=', self.to_date)]):
                        product_line = (0, 0, {
                            'date': each_coll.date,
                            'invoice_id': each_coll.invoice_id.id,
                            'partner_id': each_coll.partner_id.id,
                            'product_id': each_coll.product_id.id,
                            'company_id': each_coll.company_id.id,
                            'price_units': each_coll.price_units,
                            'uom': each_coll.uom.id,
                            'rate': each_coll.rate,
                            'credit': each_coll.credit,
                            'debit': each_coll.debit,
                            'description': each_coll.description,
                            'account_journal': each_coll.account_journal.id,
                            'account': each_coll.account.id,
                            'paid_date': each_coll.paid_date

                        })
                        today_total_cheques.append(product_line)
                else:
                    today_total_cheques = []
                    for each_coll in self.env['partner.ledger.customer'].search(
                            [('company_id', '=', self.env.user.company_id.id),('product_id','!=',False), ('date', '>=', self.from_date),
                             ('date', '<=', self.to_date)]):
                        product_line = (0, 0, {
                            'date': each_coll.date,
                            'invoice_id': each_coll.invoice_id.id,
                            'partner_id': each_coll.partner_id.id,
                            'product_id': each_coll.product_id.id,
                            'company_id': each_coll.company_id.id,
                            'price_units': each_coll.price_units,
                            'uom': each_coll.uom.id,
                            'rate': each_coll.rate,
                            'credit': each_coll.credit,
                            'debit': each_coll.debit,
                            'description': each_coll.description,
                            'account_journal': each_coll.account_journal.id,
                            'account': each_coll.account.id,
                            'paid_date': each_coll.paid_date

                        })
                        today_total_cheques.append(product_line)

                self.report_lines = today_total_cheques
            if self.report_type == 'grouped':
                self.report_lines = False
                if self.product_group:
                    today_total_cheques = []
                    for each_coll in self.env['partner.ledger.customer'].search(
                            [('company_id', '=', self.env.user.company_id.id), ('product_id','!=',False),('date', '>=', self.from_date),
                             ('date', '<=', self.to_date)]):
                        if each_coll.product_id.parent_id == self.product_group:
                            product_line = (0, 0, {
                                'date': each_coll.date,
                                'invoice_id': each_coll.invoice_id.id,
                                'partner_id': each_coll.partner_id.id,
                                'product_id': each_coll.product_id.id,
                                'company_id': each_coll.company_id.id,
                                'price_units': each_coll.price_units,
                                'uom': each_coll.uom.id,
                                'rate': each_coll.rate,
                                'credit': each_coll.credit,
                                'debit': each_coll.debit,
                                'description': each_coll.description,
                                'account_journal': each_coll.account_journal.id,
                                'account': each_coll.account.id,
                                'paid_date': each_coll.paid_date

                            })
                            today_total_cheques.append(product_line)
                else:
                    today_total_cheques = []
                    for each_coll in self.env['partner.ledger.customer'].search(
                            [('company_id', '=', self.env.user.company_id.id),('product_id','!=',False), ('date', '>=', self.from_date),
                             ('date', '<=', self.to_date)]):
                        product_line = (0, 0, {
                            'date': each_coll.date,
                            'invoice_id': each_coll.invoice_id.id,
                            'partner_id': each_coll.partner_id.id,
                            'product_id': each_coll.product_id.id,
                            'company_id': each_coll.company_id.id,
                            'price_units': each_coll.price_units,
                            'uom': each_coll.uom.id,
                            'rate': each_coll.rate,
                            'credit': each_coll.credit,
                            'debit': each_coll.debit,
                            'description': each_coll.description,
                            'account_journal': each_coll.account_journal.id,
                            'account': each_coll.account.id,
                            'paid_date': each_coll.paid_date

                        })
                        today_total_cheques.append(product_line)

                self.report_lines = today_total_cheques
        else:
            self.report_lines = False
            all = self.env['partner.ledger.customer'].search([('product_id','!=',False),('company_id', '=', self.env.user.company_id.id)]).filtered(
                lambda a: a.month == self.month)
            if all:
                if self.report_type == 'partner':
                    self.report_lines = False
                    if self.partner_id:
                        self.report_lines = False
                        today_total_cheques = []
                        for each_coll in all.filtered(lambda a: a.partner_id == self.partner_id):
                            product_line = (0, 0, {
                                'date': each_coll.date,
                                'invoice_id': each_coll.invoice_id.id,
                                'partner_id': each_coll.partner_id.id,
                                'product_id': each_coll.product_id.id,
                                'company_id': each_coll.company_id.id,
                                'price_units': each_coll.price_units,
                                'uom': each_coll.uom.id,
                                'rate': each_coll.rate,
                                'credit': each_coll.credit,
                                'debit': each_coll.debit,
                                'description': each_coll.description,
                                'account_journal': each_coll.account_journal.id,
                                'account': each_coll.account.id,
                                'paid_date': each_coll.paid_date

                            })
                            today_total_cheques.append(product_line)
                    else:
                        today_total_cheques = []
                        self.report_lines = False
                        for each_coll in all:
                            product_line = (0, 0, {
                                'date': each_coll.date,
                                'invoice_id': each_coll.invoice_id.id,
                                'partner_id': each_coll.partner_id.id,
                                'product_id': each_coll.product_id.id,
                                'company_id': each_coll.company_id.id,
                                'price_units': each_coll.price_units,
                                'uom': each_coll.uom.id,
                                'rate': each_coll.rate,
                                'credit': each_coll.credit,
                                'debit': each_coll.debit,
                                'description': each_coll.description,
                                'account_journal': each_coll.account_journal.id,
                                'account': each_coll.account.id,
                                'paid_date': each_coll.paid_date

                            })
                            today_total_cheques.append(product_line)
                    self.report_lines = today_total_cheques
                if self.report_type == 'grouped':
                    self.report_lines = False
                    if self.product_group:
                        self.report_lines = False
                        today_total_cheques = []
                        for each_coll in all:
                            if each_coll.product_id.parent_id == self.product_group:
                                product_line = (0, 0, {
                                    'date': each_coll.date,
                                    'invoice_id': each_coll.invoice_id.id,
                                    'partner_id': each_coll.partner_id.id,
                                    'product_id': each_coll.product_id.id,
                                    'company_id': each_coll.company_id.id,
                                    'price_units': each_coll.price_units,
                                    'uom': each_coll.uom.id,
                                    'rate': each_coll.rate,
                                    'credit': each_coll.credit,
                                    'debit': each_coll.debit,
                                    'description': each_coll.description,
                                    'account_journal': each_coll.account_journal.id,
                                    'account': each_coll.account.id,
                                    'paid_date': each_coll.paid_date

                                })
                                today_total_cheques.append(product_line)
                    else:
                        today_total_cheques = []
                        self.report_lines = False
                        for each_coll in all:
                            product_line = (0, 0, {
                                'date': each_coll.date,
                                'invoice_id': each_coll.invoice_id.id,
                                'partner_id': each_coll.partner_id.id,
                                'product_id': each_coll.product_id.id,
                                'company_id': each_coll.company_id.id,
                                'price_units': each_coll.price_units,
                                'uom': each_coll.uom.id,
                                'rate': each_coll.rate,
                                'credit': each_coll.credit,
                                'debit': each_coll.debit,
                                'description': each_coll.description,
                                'account_journal': each_coll.account_journal.id,
                                'account': each_coll.account.id,
                                'paid_date': each_coll.paid_date

                            })
                            today_total_cheques.append(product_line)

                    self.report_lines = today_total_cheques
                if self.report_type == 'product':
                    self.report_lines = False
                    if self.product_id:
                        self.report_lines = False
                        today_total_cheques = []
                        for each_coll in all.filtered(lambda a: a.product_id == self.product_id):
                            product_line = (0, 0, {
                                'date': each_coll.date,
                                'invoice_id': each_coll.invoice_id.id,
                                'partner_id': each_coll.partner_id.id,
                                'product_id': each_coll.product_id.id,
                                'company_id': each_coll.company_id.id,
                                'price_units': each_coll.price_units,
                                'uom': each_coll.uom.id,
                                'rate': each_coll.rate,
                                'credit': each_coll.credit,
                                'debit': each_coll.debit,
                                'description': each_coll.description,
                                'account_journal': each_coll.account_journal.id,
                                'account': each_coll.account.id,
                                'paid_date': each_coll.paid_date

                            })
                            today_total_cheques.append(product_line)
                    else:
                        today_total_cheques = []
                        self.report_lines = False
                        for each_coll in all:
                            product_line = (0, 0, {
                                'date': each_coll.date,
                                'invoice_id': each_coll.invoice_id.id,
                                'partner_id': each_coll.partner_id.id,
                                'product_id': each_coll.product_id.id,
                                'company_id': each_coll.company_id.id,
                                'price_units': each_coll.price_units,
                                'uom': each_coll.uom.id,
                                'rate': each_coll.rate,
                                'credit': each_coll.credit,
                                'debit': each_coll.debit,
                                'description': each_coll.description,
                                'account_journal': each_coll.account_journal.id,
                                'account': each_coll.account.id,
                                'paid_date': each_coll.paid_date

                            })
                            today_total_cheques.append(product_line)

                    self.report_lines = today_total_cheques


    def action_cheque_statement(self):

        return self.env.ref('ezp_cash_collection.executive_cheque_collection_id1').report_action(self)

    @api.onchange('report_type')
    def onchange_report_type(self):
        self.product_ids = False
        self.partner_id = False
        # self.vehicle_id = False
        self.product_categ = False
        self.product_groups = False


class SalesReportCompLine(models.Model):
    _name = "sale.report.custom.line"
    _description = "Sales Report Line"

    report_line = fields.Many2one('sale.report.custom')
    date = fields.Date('Date')
    paid_date = fields.Date('Paid Date')
    account = fields.Many2one('account.account')
    account_journal = fields.Many2one('account.journal')
    invoice_id = fields.Many2one('account.move', string='Invoice No')
    product_id = fields.Many2one('product.product', string='Product Name')
    partner_id = fields.Many2one('res.partner', string='Partner')
    company_id = fields.Many2one('res.company', string='company')
    description = fields.Text(string='Description')
    uom = fields.Many2one('uom.uom', string='UoM')
    price_units = fields.Float('Unit')
    rate = fields.Float('Rate')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    balance = fields.Float('Balance')

