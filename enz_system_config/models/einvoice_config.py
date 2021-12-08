from odoo import fields,models,api

class EinvoiceConfig(models.Model):
    _name = 'einvoice.config'

    name = fields.Char(default='Invoice Parameters')
    schema_id = fields.Selection([
        ('NAT', 'NAT'),
        ('TIN', 'TIN'),
        ('IQA', 'IQA'),
        ('PAS', 'PAS'),
        ('CRN', 'CRN'),
        ('MOM', 'MOM'),
        ('MLS', 'MLS'),
        ('SAG', 'SAG'),
    ], string='schemeID', required=True)
    type_of_customer = fields.Selection([
        ('b_b', 'B2B'),
        ('b_c', 'B2C')], string='Type Of Customer')
    vat_category = fields.Selection([
        ('AE', 'Vat Reverse Charge'),
        ('E', 'Exempt from Tax'),
        ('S', 'Standard rate'),
        ('Z', 'Zero rated goods'),
        ('G', 'Free export item, VAT not charged'),
        ('O', 'Services outside scope of tax'),
        ('EEA', 'VAT exempt for'),
        ('K', 'intra-community supply of goods and services'),
        ('L', 'Canary Islands general indirect tax'),
        ('M', 'Tax for production, services and importation in Ceuta and Melilla'),
        ('B', 'Transferred (VAT)'),
    ], string='VAT CATEGORY', default="AE")
    invoice_print = fields.Boolean()
    invoice_email = fields.Boolean()

    @api.onchange('type_of_customer')
    def compute_scheme_id(self):
        if self.type_of_customer == 'b_b':
            self.schema_id = 'CRN'
        if self.type_of_customer == 'b_c':
            self.schema_id = 'IQA'


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _default_einvoice_typecus(self):
        default_id = self.env['einvoice.config'].search([])
        if default_id:
            return default_id[-1].type_of_customer
        else:
            return None

    def _default_einvoice_schema_id(self):
        default_id = self.env['einvoice.config'].search([])
        if default_id:
            return default_id[-1].schema_id
        else:
            return None

    schema_id = fields.Selection([
        ('NAT', 'NAT'),
        ('TIN', 'TIN'),
        ('IQA', 'IQA'),
        ('PAS', 'PAS'),
        ('CRN', 'CRN'),
        ('MOM', 'MOM'),
        ('MLS', 'MLS'),
        ('SAG', 'SAG'),
    ], string='schemeID', required=True,default=_default_einvoice_schema_id)
    type_of_customer = fields.Selection([
        ('b_b', 'B2B'),
        ('b_c', 'B2C')], string='Type Of Customer',default=_default_einvoice_typecus)
    # vat_category = fields.Selection([
    #     ('AE', 'Vat Reverse Charge'),
    #     ('E', 'Exempt from Tax'),
    #     ('S', 'Standard rate'),
    #     ('Z', 'Zero rated goods'),
    #     ('G', 'Free export item, VAT not charged'),
    #     ('O', 'Services outside scope of tax'),
    #     ('EEA', 'VAT exempt for'),
    #     ('K', 'intra-community supply of goods and services'),
    #     ('L', 'Canary Islands general indirect tax'),
    #     ('M', 'Tax for production, services and importation in Ceuta and Melilla'),
    #     ('B', 'Transferred (VAT)'),
    # ], string='VAT CATEGORY', default="AE")

class ResCompany(models.Model):
    _inherit = 'res.company'

    def _default_einvoice_schema_id(self):
        default_id = self.env['einvoice.config'].search([])
        if default_id:
            return default_id[-1].schema_id
        else:
            return None

    schema_id = fields.Selection([
        ('NAT', 'NAT'),
        ('TIN', 'TIN'),
        ('IQA', 'IQA'),
        ('PAS', 'PAS'),
        ('CRN', 'CRN'),
        ('MOM', 'MOM'),
        ('MLS', 'MLS'),
        ('SAG', 'SAG'),
    ], string='schemeID', required=True, default=_default_einvoice_schema_id)

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _default_vat_category(self):
        default_id = self.env['einvoice.config'].search([])
        if default_id:
            return default_id[-1].vat_category
        else:
            return None

    vat_category = fields.Selection([
        ('AE', 'Vat Reverse Charge'),
        ('E', 'Exempt from Tax'),
        ('S', 'Standard rate'),
        ('Z', 'Zero rated goods'),
        ('G', 'Free export item, VAT not charged'),
        ('O', 'Services outside scope of tax'),
        ('EEA', 'VAT exempt for'),
        ('K', 'intra-community supply of goods and services'),
        ('L', 'Canary Islands general indirect tax'),
        ('M', 'Tax for production, services and importation in Ceuta and Melilla'),
        ('B', 'Transferred (VAT)'),
    ], string='VAT CATEGORY', default=_default_vat_category)

    def action_post(self):
        res = super(AccountMoveLine, self).action_post()
        self.print_einvoice()
        return res