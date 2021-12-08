from odoo import fields,models,api
# import convert_numbers
# from deep_translator import GoogleTranslator



class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    ar_quantity = fields.Char()
    ar_price = fields.Char()
    ar_price_subtotal = fields.Char()

    # @api.constrains('quantity')
    # def changequantity(self):
    #     for line in self:
    #         if line.quantity:
    #             print('1')
    #             before, after = str(line.quantity).split('.')
    #             before_int = int(before)
    #             after_int = int(after)
    #             before_ar = convert_numbers.english_to_arabic(before_int)
    #             after_ar = convert_numbers.english_to_arabic(after_int)
    #             line.ar_quantity = before_ar + '.' + after_ar
    #         else:
    #             print('1=>else')
    #             line.ar_quantity = "."
    #
    # @api.constrains('price_unit')
    # def changeprice(self):
    #     for line in self:
    #         if line.price_unit:
    #             print('2')
    #             before, after = str(line.price_unit).split('.')
    #             before_int = int(before)
    #             after_int = int(after)
    #             before_ar = convert_numbers.english_to_arabic(before_int)
    #             after_ar = convert_numbers.english_to_arabic(after_int)
    #             line.ar_price = before_ar + '.' + after_ar
    #         else:
    #             print('2:=>else')
    #             line.ar_price = "."
    #
    # @api.constrains('price_subtotal')
    # def changepricesubtotal(self):
    #     for line in self:
    #         if line.price_subtotal:
    #             print('3')
    #             before, after = str(line.price_subtotal).split('.')
    #             before_int = int(before)
    #             after_int = int(after)
    #             before_ar = convert_numbers.english_to_arabic(before_int)
    #             after_ar = convert_numbers.english_to_arabic(after_int)
    #             line.ar_price_subtotal = before_ar + '.' + after_ar
    #         else:
    #             print('3=>else')
    #             line.ar_price_subtotal = "."


class AccountMove(models.Model):
    _inherit = "account.move"

    ar_amount_total = fields.Char('Total')
    ar_amount_untaxed = fields.Char('Untaxed Amount')
    ar_amount_tax = fields.Char('Taxes')
    amount_in_word_en = fields.Char()
    amount_in_word_ar = fields.Char()
    amount_in_word_vat_en = fields.Char()
    amount_in_word_vat_ar = fields.Char()
    arabic_date = fields.Char()

    # @api.constrains('invoice_date')
    # def ar_invoice_date_value(self):
    #     for line in self:
    #         interger_part_arabic = None
    #         if line.invoice_date:
    #             m = str(line.invoice_date)
    #             if m.split('-'):
    #                 interger_part_arabic=''
    #                 for each in m.split('-'):
    #                     if interger_part_arabic:
    #                         interger_part_arabic = interger_part_arabic+'-'
    #                     interger_part_arabic += convert_numbers.english_to_arabic(int(each))
    #         line.arabic_date = interger_part_arabic
    #
    #

    # @api.constrains('amount_untaxed')
    # def total_amount_to_words(self):
    #     for invoice in self:
    #         if invoice.amount_untaxed:
    #             invoice.amount_in_word_en =  invoice.currency_id.amount_to_text(invoice.amount_untaxed)
    #         else:
    #             invoice.amount_in_word_en = ''
    #
    # @api.constrains('amount_untaxed')
    # def total_amount_to_words_arabic(self):
    #     for invoice in self:
    #         if invoice.amount_untaxed:
    #             amount_total_words = invoice.currency_id.amount_to_text(invoice.amount_untaxed)
    #             amount_arabic = GoogleTranslator(source='auto', target='ar').translate(amount_total_words)
    #             invoice.amount_in_word_ar = amount_arabic
    #         else:
    #             invoice.amount_in_word_ar = ''
    #
    # # @api.depends('amount_untaxed')
    # # def total_amount_to_words_tax_arabic(self):
    # #     for invoice in self:
    # #         if invoice.amount_total:
    # #             amount_total_words = invoice.currency_id.amount_to_text(invoice.amount_total)
    # #             amount_arabic = GoogleTranslator(source='auto', target='ar').translate(amount_total_words)
    # #             invoice.amount_in_word_vat_ar = amount_arabic
    # #         else:
    # #             invoice.amount_in_word_vat_ar = ''
    #
    # @api.constrains('amount_untaxed')
    # def total_amount_to_words_tax_english(self):
    #     for invoice in self:
    #         if invoice.amount_total:
    #             amount_total_words = invoice.currency_id.amount_to_text(invoice.amount_total)
    #             # amount_arabic = GoogleTranslator(source='auto', target='ar').translate(amount_total_words)
    #             invoice.amount_in_word_vat_en = amount_total_words
    #         else:
    #             invoice.amount_in_word_vat_en = ''
    #
    #
    #
    # @api.constrains('amount_total')
    # def total_amount_to_words_vat_arabic(self):
    #     for invoice in self:
    #         if invoice.amount_total:
    #             amount_total_words = invoice.currency_id.amount_to_text(invoice.amount_total)
    #             amount_total = GoogleTranslator(source='auto', target='ar').translate(amount_total_words)
    #             invoice.amount_in_word_vat_ar = amount_total
    #         else:
    #             invoice.amount_in_word_vat_ar = ''
    #
    # @api.constrains('amount_tax')
    # def changear_ar_amount_tax(self):
    #     for line in self:
    #         if line.amount_tax:
    #             value = line.amount_tax
    #             before, after = str(value).split('.')
    #             before_int = int(before)
    #             after_int = int(after)
    #             before_ar = convert_numbers.english_to_arabic(before_int)
    #             after_ar = convert_numbers.english_to_arabic(after_int)
    #             line.ar_amount_tax = before_ar + '.' + after_ar + ' SR'
    #         else:
    #             line.ar_amount_tax = "."
    #
    # @api.constrains('amount_total')
    # def changear_amounttotal(self):
    #     for line in self:
    #         if line.amount_total:
    #             value = line.amount_total
    #             before, after = str(value).split('.')
    #             before_int = int(before)
    #             after_int = int(after)
    #             before_ar = convert_numbers.english_to_arabic(before_int)
    #             after_ar = convert_numbers.english_to_arabic(after_int)
    #             line.ar_amount_total = before_ar + '.' + after_ar + ' SR'
    #         else:
    #             line.ar_amount_total = "."
    #
    # @api.constrains('amount_untaxed')
    # def changear_untaxamounttotal(self):
    #     for line in self:
    #         if line.amount_untaxed:
    #             value = line.amount_untaxed
    #             before, after = str(value).split('.')
    #             before_int = int(before)
    #             after_int = int(after)
    #             before_ar = convert_numbers.english_to_arabic(before_int)
    #             after_ar = convert_numbers.english_to_arabic(after_int)
    #             line.ar_amount_untaxed = before_ar + '.' + after_ar + ' SR'
    #         else:
    #             line.ar_amount_untaxed = "."
    #
