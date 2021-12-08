from odoo import fields,models,api
# import convert_numbers


class SaleOrder(models.Model):
    _inherit = "sale.order"


    ar_amount_total = fields.Char('Total')
    ar_amount_untaxed = fields.Char('Untaxed Amount')
    ar_amount_tax = fields.Char('Taxes')

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
    #
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

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    ar_price = fields.Char()
    ar_price_subtotal = fields.Char()
    ar_qty = fields.Char()
    ar_qty_invoiced = fields.Char()

    # @api.constrains('product_uom_qty')
    # def changequantity(self):
    #     for line in self:
    #         if line.product_uom_qty:
    #             before, after = str(line.product_uom_qty).split('.')
    #             before_int = int(before)
    #             after_int = int(after)
    #             before_ar = convert_numbers.english_to_arabic(before_int)
    #             after_ar = convert_numbers.english_to_arabic(after_int)
    #             line.ar_qty = before_ar + '.' + after_ar
    #         else:
    #             line.ar_qty = "."
    #
    # @api.constrains('qty_invoiced')
    # def changequantityinv(self):
    #     for line in self:
    #         if line.qty_invoiced:
    #             before, after = str(line.qty_invoiced).split('.')
    #             before_int = int(before)
    #             after_int = int(after)
    #             before_ar = convert_numbers.english_to_arabic(before_int)
    #             after_ar = convert_numbers.english_to_arabic(after_int)
    #             line.ar_qty_invoiced = before_ar + '.' + after_ar
    #         else:
    #             line.ar_qty_invoiced = "."
    #
    # @api.constrains('price_unit')
    # def changeprice(self):
    #     for line in self:
    #         if line.price_unit:
    #             before, after = str(line.price_unit).split('.')
    #             before_int = int(before)
    #             after_int = int(after)
    #             before_ar = convert_numbers.english_to_arabic(before_int)
    #             after_ar = convert_numbers.english_to_arabic(after_int)
    #             line.ar_price = before_ar + '.' + after_ar
    #         else:
    #             line.ar_price = "."
    #
    # @api.constrains('price_subtotal')
    # def changepricesubtotal(self):
    #     for line in self:
    #         if line.price_subtotal:
    #             before, after = str(line.price_subtotal).split('.')
    #             before_int = int(before)
    #             after_int = int(after)
    #             before_ar = convert_numbers.english_to_arabic(before_int)
    #             after_ar = convert_numbers.english_to_arabic(after_int)
    #             line.ar_price_subtotal = before_ar + '.' + after_ar
    #         else:
    #             line.ar_price_subtotal = "."
