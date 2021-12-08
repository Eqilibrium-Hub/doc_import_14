from odoo import fields,models

class WorkshopServices(models.Model):
    _name = 'workshop.services'

    name = fields.Char()
    price = fields.Char()
    product_id = fields.Many2one('product.product')
    state = fields.Selection([('draft','Draft'),('created','Created')],default='draft')

    def create_product(self):
        self.product_id = self.env['product.template'].create({
            'name':self.name,
            'type':'service',
            'list_price':self.price,
            'invoice_policy':'order',
        }).product_variant_id.id
        self.state = 'created'

class WorkshopComplaints(models.Model):
    _name = 'workshop.complaints'

    name = fields.Char()

class WorkshopSolutions(models.Model):
    _name = 'workshop.solutions'

    name = fields.Char()

class VehicleBrand(models.Model):
    _name = 'vehicle.brand'

    name = fields.Char('Brand')
    model = fields.Char()

class VehicleConfig(models.Model):
    _name = 'vehicle.config'

    name = fields.Char('Vehilce No')
    customer_id = fields.Many2one('res.partner')
    brand_id = fields.Many2one('vehicle.brand')


