from  uuid import uuid4
from odoo import models,fields






#
# class ResCompany(models.Model):
#     _inherit = 'res.company'
#
#     schema_id = fields.Selection([
#         ('CRN', 'CRN'),
#         ('MOM', 'MOM'),
#         ('MLS', 'MLS'),
#         ('SAG', 'SAG'),
#         ('OTH', 'OTH')
#     ], string='schemeID', required=True)
#     schema_id_no = fields.Char(string="Schema No")
#
#
#
# class ResPartner(models.Model):
#     _inherit = 'res.partner'
#
#
#     building_no = fields.Char(string="BuildingNumber")
#     plot_id = fields.Char(string="PlotIdentification")
#
#     schema_id = fields.Selection([
#         ('NAT', 'NAT'),
#         ('TIN', 'TIN'),
#         ('IQA', 'IQA'),
#         ('PAS', 'PAS'),
#         ('CRN', 'CRN'),
#         ('MOM', 'MOM'),
#         ('MLS', 'MLS'),
#         ('SAG', 'SAG'),
#     ], string='schemeID', required=True)
#     schema_id_no = fields.Char(string="Schema No")
#     type_of_customer = fields.Selection([
#         ('b_b', 'B2B'),
#         ('b_c', 'B2C')],string='Type Of Customer')
#
# class AccountMoveLine(models.Model):
#     _inherit = "account.move.line"
#
#     vat_category = fields.Selection([
#         ('AE', 'Vat Reverse Charge'),
#         ('E', 'Exempt from Tax'),
#         ('S', 'Standard rate'),
#         ('Z', 'Zero rated goods'),
#         ('G', 'Free export item, VAT not charged'),
#         ('O', 'Services outside scope of tax'),
#         ('EEA', 'VAT exempt for'),
#         ('K', 'intra-community supply of goods and services'),
#         ('L', 'Canary Islands general indirect tax'),
#         ('M', 'Tax for production, services and importation in Ceuta and Melilla'),
#         ('B', 'Transferred (VAT)'),
#     ], string='VAT CATEGORY',default="AE")
