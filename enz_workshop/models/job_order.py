from odoo import fields,models,api,_
from odoo.tests.common import Form
from datetime import datetime,date


class JobOrder(models.Model):
    _name = 'job.order'
    _order = 'id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('jo.no') or '/'

        res = super(JobOrder, self).create(vals)
        return res

    name = fields.Char(string='Event No', required=True, index=True, copy=False, default='New', readonly=1)
    vehicle_id = fields.Many2one('vehicle.config')
    customer_id = fields.Many2one('res.partner')
    state = fields.Selection([('draft','Draft'),('approved','Approved'),('done','Done'),('invoiced','Invoiced')],default='draft')
    complaint_lines = fields.One2many('complaint.lines','job_id')
    spare_part_lines = fields.One2many('spare.parts','job_id')
    vehicle_services_lines = fields.One2many('vehicle.services','job_id')
    sale_id = fields.Many2one('sale.order')
    invoice_id = fields.Many2one('account.move')
    invoice_count = fields.Boolean()
    sale_count = fields.Boolean()
    date = fields.Date(default=datetime.now().date())
    delivery_date = fields.Date()

    @api.onchange('vehicle_id')
    def compute_customer(self):
        self.customer_id = self.vehicle_id.customer_id.id

    def view_invoice(self):
        contract_obj = self.env['account.move'].search([('id', '=', self.invoice_id.id)])
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
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.move',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Invoice'),
                    'res_id': contract_ids
                }

            return value

    def view_so(self):
        contract_obj = self.env['sale.order'].search([('id', '=', self.sale_id.id)])
        contract_ids = []
        for each in contract_obj:
            contract_ids.append(each.id)
        view_id = self.env.ref('sale.view_order_form').id
        if contract_ids:
            if len(contract_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Sale Order'),
                    'res_id': contract_ids and contract_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', contract_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Sale Order'),
                    'res_id': contract_ids
                }

            return value


    def approve(self):
        self.state = 'approved'

    def done(self):
        self.state = 'done'

    def create_invoice(self):
        sale_list = []
        for line in self.spare_part_lines:
            sale_line = (0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'price_unit': line.unit_price,
                'name': line.product_id.name,
                'product_uom': line.product_id.uom_id.id,
                'tax_id': [(6, 0, line.tax_ids.ids)]
            })
            sale_list.append(sale_line)
        for line2 in self.vehicle_services_lines:
            sale_line = (0, 0, {
                'product_id': line2.service_id.product_id.id,
                'product_uom_qty': 1,
                'price_unit': line2.price,
                'name': line2.service_id.product_id.name,
                'product_uom': line2.service_id.product_id.uom_id.id,
                'tax_id': [(6, 0, line2.tax_ids.ids)]
            })
            sale_list.append(sale_line)
        sale_id = self.env['sale.order'].create({
            'partner_id': self.customer_id.id,
            'order_line': sale_list,
        })
        self.sale_id = sale_id.id
        sale_id.action_confirm()
        picking = self.env['stock.picking'].search([('sale_id', '=', self.sale_id.id)])
        if picking:
            for line in picking:
                # line.action_view_picking()
                m = line.button_validate()
                Form(self.env['stock.immediate.transfer'].with_context(m['context'])).save().process()
        self.invoice_id = sale_id._create_invoices()
        self.state = 'invoiced'
        self.sale_count = True
        self.invoice_count = True


class ComplaintLines(models.Model):
    _name = 'complaint.lines'

    job_id = fields.Many2one('job.order')
    compalint_id = fields.Many2one('workshop.complaints')
    solutions = fields.Many2one('workshop.solutions')

class SpareParts(models.Model):
    _name = 'spare.parts'

    job_id = fields.Many2one('job.order')
    product_id = fields.Many2one('product.product')
    unit_price = fields.Float()
    quantity = fields.Float(default=1)
    tax_ids = fields.Many2many('account.tax',domain=[('type_tax_use','=','sale')])
    sub_total = fields.Float()

    @api.onchange('product_id')
    def compute_values(self):
        self.unit_price = self.product_id.lst_price
        self.tax_ids = [(6,0,self.product_id.taxes_id.ids)]

    @api.onchange('unit_price','quantity')
    def compute_subtotal(self):
        self.sub_total = self.unit_price * self.quantity

class VehicleServices(models.Model):
    _name = 'vehicle.services'

    job_id = fields.Many2one('job.order')
    service_id = fields.Many2one('workshop.services')
    tax_ids = fields.Many2many('account.tax',domain=[('type_tax_use','=','sale')])
    price = fields.Float()

    @api.onchange('service_id')
    def compute_values(self):
        self.price = self.service_id.price
