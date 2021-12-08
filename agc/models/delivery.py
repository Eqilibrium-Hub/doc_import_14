from odoo import fields,models,api,_
from datetime import datetime,date
from odoo.exceptions import UserError

class GalvDeliveryForm(models.Model):
    _name = 'galv.delivery.form'
    _order = 'id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('galv.delivery.no') or '/'

        res = super(GalvDeliveryForm, self).create(vals)
        return res

    name = fields.Char(string='Event No', required=True, index=True, copy=False, default='New', readonly=1)
    date = fields.Date(default=datetime.now().date())
    partner_id = fields.Many2one('res.partner')
    po_no = fields.Char('P.O')
    job = fields.Char('JOB')
    lot_no = fields.Char('LOT No')
    dc_no = fields.Char('DC-No')
    driver_id = fields.Char()
    driver_mobile = fields.Char()
    truck_no = fields.Char()
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    wbs_no = fields.Char('Weight Bridge Slip No')
    delivery_lines = fields.One2many('galv.delivery.lines','delivery_id')
    state = fields.Selection([('draft','Draft'),('done','Done'),('invoiced','Invoiced')],default='draft')
    invoice_id = fields.Many2one('account.move')
    total_weight_before_galv = fields.Float('Total Weight Before Galvanization')
    total_weight_after_galv = fields.Float('Total Weight After Galvanization')
    total_no_of_pices_galv = fields.Float('Total No. Of Pieces')

    # @api.onchange('driver_id')
    # def compute_mobile(self):
    #     self.driver_mobile = self.driver_id.mobile

    def done(self):
        self.state = 'done'

    def create_invoice(self):
        if not self.partner_id.id:
            raise UserError('Please Enter the Customer Details')
        else:
            invoice_list = []
            tax = None
            tax_details = self.env['account.tax'].search([('name','=','Vat 15%'),('type_tax_use','=','sale')])
            if tax_details:
                tax = [(6, 0, tax_details.ids)]
            for so_line in self.delivery_lines:
                invoice_list.append((0, 0, {
                    'name': so_line.name.name,
                    'job_no':so_line.job_no,
                    'date_of_supply':self.date,
                    'price_unit':0,
                    'quantity': so_line.wag,
                    'no_of_pices':so_line.no_of_pices,
                    'product_uom_id': so_line.product_id.uom_id.id,
                    'product_id': so_line.product_id.id,
                    'tax_ids': tax}))
            account_move = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'delivery_note_no':self.id,
                'partner_id': self.partner_id.id,
                'invoice_line_ids': invoice_list,
                'company_id': self.env.user.company_id.id,
            })
            self.state = 'invoiced'
            self.invoice_id = account_move.id
            contract_obj = self.invoice_id
            contract_ids = []
            for each in contract_obj:
                contract_ids.append(each.id)
            view_id = self.env.ref('account.view_move_form').id
            if contract_ids:
                if len(contract_ids) <= 1:
                    value = {
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'account.move',
                        'view_id': view_id,
                        'type': 'ir.actions.act_window',
                        'name': _('Invoice'),
                        'res_id': contract_ids and contract_ids[0]
                    }
                else:
                    value = {
                        'domain': str([('id', 'in', contract_ids)]),
                        'view_mode': 'kanban,form',
                        'res_model': 'account.move',
                        'view_id': False,
                        'type': 'ir.actions.act_window',
                        'name': _('Invoice'),
                        'res_id': contract_ids
                    }

                return value
    # def search_values(self):
    #     m = name
    #     value = (self.env['galv.delivery.form'].search([(m,'=',self.name)]))
    #     for line in self.env['galv.delivery.lines'].search([('delivery_id','=',value.id)]):
    #         print(line.m)
    #     print(self.env['galv.delivery.lines'].search([('delivery_id','=',value.id)])[m])

    def view_invoice(self):
        contract_obj = self.invoice_id
        contract_ids = []
        for each in contract_obj:
            contract_ids.append(each.id)
        view_id = self.env.ref('account.view_move_form').id
        if contract_ids:
            if len(contract_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'account.move',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'res_id': contract_ids and contract_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', contract_ids)]),
                    'view_mode': 'kanban,form',
                    'res_model': 'account.move',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'res_id': contract_ids
                }

            return value


class GalvDeliveryLines(models.Model):
    _name = 'galv.delivery.lines'

    delivery_id = fields.Many2one('galv.delivery.form')
    job_no = fields.Char()
    product_id = fields.Many2one('product.product',string='Scope of Work')
    name = fields.Many2one('description.configuration')
    wbg = fields.Float('Weight Before Galvanization')
    wag = fields.Float('Weight After Galvanization')
    no_of_pices = fields.Float('No.of Pieces')

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    job_no = fields.Char(force_save=True)