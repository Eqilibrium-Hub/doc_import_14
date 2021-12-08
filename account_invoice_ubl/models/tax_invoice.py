from odoo import fields, models, api
from datetime import datetime, timedelta
# from googletrans import Translator
# import convert_numbers
from  uuid import uuid4

# translator = Translator(service_urls=['translate.googleapis.com'])
import werkzeug.urls

try:
    import qrcode
except ImportError:
    qrcode = None


class TaxInvoice(models.Model):
    _inherit = 'account.move'
    datetime_field = fields.Datetime(string="Create Date",default=lambda self: fields.Datetime.now())
    decoded_data = fields.Char(string="Decoded Data")
    debit_note = fields.Boolean(default=False)
    credit_note = fields.Boolean(default=False)
    qr_image = fields.Binary(string="QR Image")
    uuid = fields.Char('UUID', size=50, index=True, default=lambda self: str(uuid4()), copy=False)

    @api.depends('invoice_date')
    def out_refund_date(self):
        if self.move_type == 'out_refund':
            self.credit_note =True
        else:
            self.credit_note = False

    @api.depends('invoice_date')
    def invoices_date(self):
        if self.debit_origin_id:
            self.debit_note =True
        else:
            self.debit_note =False




    def print_system_date(self):
        return datetime.now()

    def ar_price_subtotal(self, l):
        if l.tax_ids:
            v = (15 / 100) * l.price_subtotal
            # stringtotranslate = l.price_subtotal+ v

            stringtotranslate = int(l.price_subtotal + v)
            # self.ar_price_subtotal = int(l.price_subtotal + v)
            # translated_string = convert_numbers.english_to_arabic(stringtotranslate)
            # print(translated_string)
            # if translated_string == 'خاطئة':
            #     return stringtotranslate
            # else:
            #     return translated_string

    def price_subtotal(self, l):
        if l.tax_ids:
            return l.price_subtotal+(15 / 100) * l.price_subtotal
        else:
            return l.price_subtotal
    def taxable_amount(self, l):
            if l.tax_ids:
                return (15 / 100) * l.price_subtotal
            else:
                return 0

    # def _convert_image(self, im):
    #     """ Parse image and prepare it to a printable format """
    #     pixels = []
    #     pix_line = ""
    #     im_left = ""
    #     im_right = ""
    #     switch = 0
    #     img_size = [0, 0]
    #
    #     if im.size[0] > 512:
    #         print("WARNING: Image is wider than 512 and could be truncated at print time ")
    #     if im.size[1] > 255:
    #         raise ImageSizeError()
    #
    #     im_border = self._check_image_size(im.size[0])
    #     for i in range(im_border[0]):
    #         im_left += "0"
    #     for i in range(im_border[1]):
    #         im_right += "0"
    #
    #     for y in range(im.size[1]):
    #         img_size[1] += 1
    #         pix_line += im_left
    #         img_size[0] += im_border[0]
    #         for x in range(im.size[0]):
    #             img_size[0] += 1
    #             RGB = im.getpixel((x, y))
    #             im_color = (RGB[0] + RGB[1] + RGB[2])
    #             im_pattern = "1X0"
    #             pattern_len = len(im_pattern)
    #             switch = (switch - 1) * (-1)
    #             for x in range(pattern_len):
    #                 if im_color <= (255 * 3 / pattern_len * (x + 1)):
    #                     if im_pattern[x] == "X":
    #                         pix_line += "%d" % switch
    #                     else:
    #                         pix_line += im_pattern[x]
    #                     break
    #                 elif im_color > (255 * 3 / pattern_len * pattern_len) and im_color <= (255 * 3):
    #                     pix_line += im_pattern[-1]
    #                     break
    #         pix_line += im_right
    #         img_size[0] += im_border[1]
    #
    #     return (pix_line, img_size)
    #
    # def qr(self):
    #     """ Print QR Code for the provided string """
    #     text ='MOunika TEsting'
    #     qr_code = qrcode.QRCode(version=4, box_size=4, border=1)
    #     qr_code.add_data(text)
    #     qr_code.make(fit=True)
    #     qr_img = qr_code.make_image()
    #     im = qr_img._img.convert("RGB")
    #     # Convert the RGB image in printable image
    #     return self._convert_image(im)

    @api.model
    def build_qr_code_url(self, amount, comment):
        communication = ""
        if comment:
            communication = (comment[:137] + '...') if len(comment) > 140 else comment
        qr_code_string = 'BCD\n001\n1\nSCT\n%s\n%s\n%s\nEUR%s\n\n\n%s' % (
        self.partner_id.name, self.company_id.name, self.partner_id.name, amount, communication)
        qr_code_url = ('QR', werkzeug.url_quote_plus(qr_code_string), 128, 128)
        return qr_code_url

    # def testing(self):
    #     # return 'Seller Name:'+self.company_id.name + ','+'Seller VAT:' + str(self.company_id.vat) +',' +'Time Stamp Of Invoice:' +str(self.create_date) + ','+'VAT Total:'+str(self.amount_tax)+'Electronic Invoice Total:'+str(self.amount_total)
    #     return 'Seller Name:'+self.company_id.name + '\n'+'Seller VAT:' + str(self.company_id.vat) +'\n' +'Time Stamp Of Invoice:' +str(self.create_date) +'\n'+'VAT Total:'+str(self.amount_tax)+'\n'+'Electronic Invoice Total:'+str(self.amount_total)


    # def testing(self):
    #     data = "BROTHERS GROUP55"+"300090000000003"+"2021-11-05T13:45:38"+"9.00'+'1.18"
    #     # data = "  BROTHERS GROUP     300090000000003  2021-11-08T13:45:38  9.00  1.18"
    #     # data = ""+"BROTHERS GROUP   "+""+"300090000000003"+""+"2021-11-08"+"T"+"13:45:38"+""+"9.00"+""+"1.18"
    #     leng = len(self.company_id.name)
    #     company_name = self.company_id.name
    #     if 17 > leng:
    #         for r in range(17-leng):
    #             if len(company_name) != 17:
    #                company_name +=' '
    #             else:
    #                 break
    #     else:
    #         if 17 < leng:
    #             company_name = company_name[:17]
    #
    #
    #     data = ""+str(company_name)+""+str(self.company_id.vat)+""+str(self.invoice_date)+"T"+str(self.datetime_field.time())+""+str(self.amount_total)+""+str(self.amount_tax)
    #     import base64
    #     mou = base64.b64encode(bytes(data, 'utf-8'))
    #     # print(str(mou),'888888888888')
    #     # print(mou.decode(),'111888888888888')
    #     # mou =
    #     #
    #     # qr_image = base64.b64encode(data)
    #     # # self.qr_code_image = qr_image
    #     # # print(base64.b64decode(data),'jjjjjjjjjjjjjjjjjj')
    #     # print(self.qr_code_image.decode())
    #     # print(base64.b64decode(data))
    #
    #     return str(mou.decode())
    #
    #     # return 'ARFCUk9USEVSUyBHUk9VUCAgIAIPMzAwMDkwMDAwMDAwMDAzAxMyMDIxLTExLTA4VDEzOjQ1OjM4BAQ5LjAwBQQxLjE4'
    # def testing(self):
    #     # data = "\n BROTHERS GROUP55\n"+"\n300090000000003\n"+"\n2021-11-05T13:45:38\n"+"\n9.00'+'\n1.18"
    #     # data = "  BROTHERS GROUP     300090000000003  2021-11-08T13:45:38  9.00  1.18"
    #     # data = ""+"BROTHERS GROUP   "+""+"300090000000003"+""+"2021-11-08"+"T"+"13:45:38"+""+"9.00"+""+"1.18"
    #     leng = len(self.company_id.name)
    #     company_name = self.company_id.name
    #     if 17 > leng:
    #         for r in range(17-leng):
    #             if len(company_name) != 17:
    #                company_name +=' '
    #             else:
    #                 break
    #     else:
    #         if 17 < leng:
    #             company_name = company_name[:17]
    #     vat_leng = len(self.company_id.vat)
    #     vat_name = self.company_id.vat
    #     if 17 > vat_leng:
    #         for r in range(15 - vat_leng):
    #             if len(vat_name) != 15:
    #                 vat_name += ' '
    #             else:
    #                 break
    #     else:
    #         if 17 < leng:
    #             vat_name = vat_name[:17]
    #
    #     amount_total = str(round(self.amount_total))
    #     amount_leng = len(str(round(self.amount_total)))
    #     if len(amount_total) < 17:
    #         for r in range(17-amount_leng):
    #             if len(amount_total) != 17:
    #                amount_total +=' '
    #             else:
    #                 break
    #
    #     tax_leng = len(str(round(self.amount_tax)))
    #     amount_tax_total = str(round(self.amount_tax))
    #     if len(amount_tax_total) < 17:
    #         for r in range(17-tax_leng):
    #             if len(amount_tax_total) != 17:
    #                amount_tax_total +=' '
    #             else:
    #                 break
    #
    #
    #     # print("The number of digits in the number are:", amount_total)
    #
    #     # data = ""+'Salah Hospital'+""+'31012239350000311123'+""+'2023-01-01'+"T"+str(self.datetime_field.time())+""+str(200.00)+""+str(-125.00)
    #     # data = ""+str(company_name)+""+str(self.company_id.vat)+""+str(self.invoice_date)+"T"+str(self.datetime_field.time())+""+str(self.amount_total)+""+str(self.amount_tax)
    #     # data = ""+str(company_name)+""+str(self.company_id.vat)+""+str(self.invoice_date)+"T"+str(self.datetime_field.time())+""+str(self.amount_total)+""+str(self.amount_tax)+""+'nMkXME2tSovykLKU6VUnIq8667SMCoc6A7tKcMKpY0 ='+""+"3056301006072"
    #     # data = ""+str(company_name)+""+str(self.company_id.vat)+""+str(self.invoice_date)+"T"+str(self.datetime_field.time())+"Z"+""+str(self.amount_total)+""+str(self.amount_tax)
    #
    #
    #
    #     # data = ""+str(company_name)+""+str(self.company_id.vat)+""+str(self.invoice_date)+"T"+str(self.datetime_field.time())+"Z"+""+amount_total+""+amount_tax_total
    #
    #     data = ""+str(company_name)+""+str(vat_name)+""+str(self.invoice_date)+"T"+str(self.datetime_field.time())+"Z"+""+amount_total+""+amount_tax_total
    #     print(str(int(self.amount_total)))
    #     import base64
    #     mou = base64.b64encode(bytes(data, 'utf-8'))
    #     # print(str(mou),'888888888888')
    #     # print(mou.decode(),'111888888888888')
    #     # mou =
    #     #
    #     # qr_image = base64.b64encode(data)
    #     # # self.qr_code_image = qr_image
    #     # # print(base64.b64decode(data),'jjjjjjjjjjjjjjjjjj')
    #     # print(self.qr_code_image.decode())
    #     # print(base64.b64decode(data))
    #     self.decoded_data =str(mou.decode())
    #     # test =mou.decode('ascii')
    #     # print(self.decoded_data,'decoded_data')
    #     # print(test,'test')
    #
    #     ####below 3 working
    #     # return 'AQpGaXJzdCBTaG9wAg8zMTAxODkzNzU5MjAwMDMDFDIwMjEtMDEtMDVUMDk6MzI6NDBaBAYyNTAuMDAFBDEwLjAwBkA4YjBhNWY5OWFkNjIxM2Y1ZmRiYTNmMmRiOGY5ODlmYjk5MmMwYWI0ODZhMjkyMmIyMjFiMTViYzg2Mzg5ZDVh'
    #     # return 'ARFGaXJzdCBTaG9wICAgICAgIAIPMzEwMTg5Mzc1OTIwMDAzAxQyMDIxLTAxLTA1VDA5OjMyOjQwWgQGMjUwLjAwBQQxMC4wMAZAOGIwYTVmOTlhZDYyMTNmNWZkYmEzZjJkYjhmOTg5ZmI5OTJjMGFiNDg2YTI5MjJiMjIxYjE1YmM4NjM4OWQ1YQ=='
    #     # return 'ARFGaXJzdCBTaG9wICAgICAgIAIPMzEwMTg5Mzc1OTIwMDAzAxQyMDIxLTAxLTA1VDA5OjMyOjQwWgQGMTI1OTAwBQY2MDAwMDAGQDhiMGE1Zjk5YWQ2MjEzZjVmZGJhM2YyZGI4Zjk4OWZiOTkyYzBhYjQ4NmEyOTIyYjIyMWIxNWJjODYzODlkNWE='
    #
    #     #
    #     #
    #     # First
    #     # Shop       3101893759200032021 - 01 - 05
    #     # T09: 32:40
    #     # Z250.0010.00
    #     #
    #     # @8
    #     #
    #     # b0a5f99ad6213f5fdba3f2db8f989fb992c0ab486a2922b221b15bc86389d5a
    #     print(mou.decode())
    #
    #     return str(mou.decode())
    #
    #     # return 'ARFCUk9USEVSUyBHUk9VUCAgIAIPMzAwMDkwMDAwMDAwMDAzAxMyMDIxLTExLTA4VDEzOjQ1OjM4BAQ5LjAwBQQxLjE4'
    def testing(self):
        leng = len(self.company_id.name)
        company_name = self.company_id.name
        if 42 > leng:
            for r in range(42-leng):
                if len(company_name) != 42:
                   company_name +=' '
                else:
                    break
        else:
            if 42 < leng:
                company_name = company_name[:42]
        vat_leng = len(self.company_id.vat)
        vat_name = self.company_id.vat
        if 17 > vat_leng:
            for r in range(15 - vat_leng):
                if len(vat_name) != 15:
                    vat_name += ' '
                else:
                    break
        else:
            if 17 < leng:
                vat_name = vat_name[:17]

        amount_total = str(self.amount_total)
        amount_leng = len(str(self.amount_total))
        if len(amount_total) < 17:
            for r in range(17-amount_leng):
                if len(amount_total) != 17:
                   amount_total +=' '
                else:
                    break

        tax_leng = len(str(self.amount_tax))
        amount_tax_total = str(self.amount_tax)
        if len(amount_tax_total) < 17:
            for r in range(17-tax_leng):
                if len(amount_tax_total) != 17:
                   amount_tax_total +=' '
                else:
                    break
        data = "*"+str(company_name)+""+str(vat_name)+""+str(self.invoice_date)+"T"+str(self.datetime_field.time())+"Z"+""+amount_total+""+amount_tax_total
        import base64
        mou = base64.b64encode(bytes(data, 'utf-8'))
        self.decoded_data =str(mou.decode())

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=20,
            border=4,
        )
        data_im = str(mou.decode())
        qr.add_data(data_im)
        qr.make(fit=True)
        img = qr.make_image()

        import io
        import base64

        temp = io.BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.qr_image = qr_image

        return str(mou.decode())



class ResCompany(models.Model):
    _inherit = 'res.company'

    schema_id = fields.Selection([
        ('CRN', 'CRN'),
        ('MOM', 'MOM'),
        ('MLS', 'MLS'),
        ('SAG', 'SAG'),
        ('OTH', 'OTH')
    ], string='schemeID', required=True)
    schema_id_no = fields.Char(string="Schema No")



class ResPartner(models.Model):
    _inherit = 'res.partner'


    building_no = fields.Char(string="BuildingNumber")
    plot_id = fields.Char(string="PlotIdentification")

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
    schema_id_no = fields.Char(string="Schema No")
    type_of_customer = fields.Selection([
        ('b_b', 'B2B'),
        ('b_c', 'B2C')],string='Type Of Customer')


    @api.onchange('type_of_customer')
    def onchange_type_of_customer(self):
        if self.type_of_customer == "b_c":
            self.schema_id = "IQA"
        if self.type_of_customer == "b_b":
            self.schema_id = "CRN"
    @api.onchange('company_type')
    def onchange_type_company_type(self):
        if self.company_type == "company":
            self.type_of_customer ="b_b"
        else:
            self.type_of_customer = "b_c"
