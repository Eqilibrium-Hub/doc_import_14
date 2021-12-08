from odoo import fields,models,api
# import convert_numbers
# from deep_translator import GoogleTranslator



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    ar_name = fields.Char()
    ar_list = fields.Char()

    # @api.onchange('list_price')
    # def ar_listpricecompute(self):
    #     if self.list_price:
    #         value = self.list_price
    #         before, after = str(value).split('.')
    #         before_int = int(before)
    #         after_int = int(after)
    #         before_ar = convert_numbers.english_to_arabic(before_int)
    #         after_ar = convert_numbers.english_to_arabic(after_int)
    #         self.ar_list = before_ar + '.' + after_ar

    #
    # @api.onchange('name')
    # def ar_namecompute(self):
    #     if self.name:
    #         translated = GoogleTranslator(source='auto', target='ar').translate(self.name)
    #         self.ar_name = translated