from odoo import fields,models,api
# import convert_numbers
# from deep_translator import GoogleTranslator




class Partner(models.Model):
    _inherit = 'res.partner'

    ar_name = fields.Char()
    ar_street = fields.Char()
    ar_street2 = fields.Char()
    ar_city = fields.Char()
    ar_state = fields.Char()
    ar_zip = fields.Char()
    ar_country = fields.Char()
    ar_phone = fields.Char()
    ar_tax_id = fields.Char()

    # @api.onchange('name')
    # def compute_ar_name(self):
    #     if self.name:
    #         translated = GoogleTranslator(source='auto', target='ar').translate(self.name)
    #         self.ar_name = translated


    # @api.onchange('street')
    # def computear_street(self):
    #     if self.street:
    #         translated = GoogleTranslator(source='auto', target='ar').translate(self.street)
    #         self.ar_street = translated

    # @api.onchange('street2')
    # def computear_street2(self):
    #     if self.street:
    #         translated = GoogleTranslator(source='auto', target='ar').translate(self.street2)
    #         self.ar_street2 = translated

    # @api.onchange('city')
    # def computear_city(self):
    #     if self.street:
    #         translated = GoogleTranslator(source='auto', target='ar').translate(self.city)
    #         self.ar_city = translated

    # @api.onchange('state_id')
    # def computear_state(self):
    #     if self.state_id.id:
    #         translated = GoogleTranslator(source='auto', target='ar').translate(self.state_id.name)
    #         self.ar_state = translated

    # @api.onchange('country_id')
    # def computear_country(self):
    #     if self.country_id.id:
    #         translated = GoogleTranslator(source='auto', target='ar').translate(self.country_id.name)
    #         self.ar_country = translated

    # @api.onchange('zip')
    # def computear_zip(self):
    #     if self.zip:
    #         a = self.zip
    #         self.ar_zip = convert_numbers.english_to_arabic(a)
    #

    # @api.onchange('phone')
    # def ar_phonecompute(self):
    #     if self.phone:
    #         a = self.phone
    #         self.ar_phone = convert_numbers.english_to_arabic(a)

    # @api.onchange('vat')
    # def ar_taxidcomputeii(self):
    #     if self.vat:
    #         a = int(self.vat)
    #         self.ar_tax_id = convert_numbers.english_to_arabic(a)