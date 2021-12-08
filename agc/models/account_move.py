from odoo import models,fields


class AccountMove(models.Model):
    _inherit = 'account.move'


    po_number = fields.Char('PO Number')
    po_date = fields.Date('PO Date')
    delivery_note_no = fields.Many2one('galv.delivery.form',string='Delivery Note No')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    date_of_supply = fields.Date('Date of Supply',force_save=True)
    no_of_pices = fields.Float('No.of Pieces')


class ResCompany(models.Model):
    _inherit = 'res.company'

    footer_image = fields.Image('Footer Image 1')
    industry_no = fields.Char('Industrial License No',store=True)
    # footer_images = fields.Image('Footer Image 2')



