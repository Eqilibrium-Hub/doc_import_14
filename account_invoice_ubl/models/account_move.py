# Copyright 2016-2017 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging

from lxml import etree
from odoo import models, fields, api
from odoo.tools import float_is_zero, float_round

logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "base.ubl"]


    ubl_preview = fields.Integer(string="Test")




    # def action_post(self):
    #     res = super(AccountMove, self).action_post()
        # if self.move_type != 'in_invoice' and self.move_type != 'in_refund':
        # #if self.move_type != 'in_invoice':
        #     m=self.attach_ubl_xml_file_button()
        #     self.ubl_preview = 1
        # else:
        #     ''
        # return res


    def view_attachments(self):
        # "res_id": self.id,
        # "res_model": self._name,
        attach = self.env['ir.attachment'].search([('res_id','=',self.id),("res_model",'=',self._name)])
        action = self.env["ir.attachment"].action_get()
        action.update({"res_id": attach.id, "views": False, "view_mode": "form,tree"})
        return action

    def _ubl_add_header(self, parent_node, ns, version="2.1"):
        self.ensure_one()
        # self._ubl_ext_header(parent_node, ns, version="2.1")
        #######code added##################3333
        # ext_ubls = etree.SubElement(parent_node, ns["ext"] + "UBLExtensions")
        # ext_ubl = etree.SubElement(ext_ubls, ns["ext"] + "UBLExtension")
        # ext_url_ubl = etree.SubElement(ext_ubl, ns["ext"] + "ExtensionURI")
        # ext_url_ubl.text = "urn:oasis:names:specification:ubl:dsig:enveloped:xades"
        # ext_content_ubl = etree.SubElement(ext_ubls, ns["ext"] + "ExtensionContent")
        # ext_content_ubl = etree.SubElement(ext_content_ubl, ns["sig"] + "ExtensionContent")





        ##########commented##########################
        # ubl_versions = etree.SubElement(parent_node, ns["ext"] + "UBLExtensions")
        # ubl_versions = etree.SubElement(parent_node, ns["ext"] + "UBLVersionID")
        # # ubl_versions.text = "tgtytr"
        # ubl_version = etree.SubElement(ubl_versions, ns["cbc"] + "UBLVersionID")
        # ubl_version.text = version
        #########################################
        profile_id = etree.SubElement(parent_node, ns["cbc"] + "ProfileID")
        profile_id.text = "reporting:1.0"
        doc_id = etree.SubElement(parent_node, ns["cbc"] + "ID")
        doc_id.text = self.name
        uuid_no = etree.SubElement(parent_node, ns["cbc"] + "UUID")
        uuid_no.text = self.uuid
        issue_date = etree.SubElement(parent_node, ns["cbc"] + "IssueDate")
        issue_date.text = self.invoice_date.strftime("%Y-%m-%d")
        issue_time = etree.SubElement(parent_node, ns["cbc"] + "IssueTime")
        issue_time.text = str(self.datetime_field.time())
        code = ""
        code_b = ""
        if self.partner_id.type_of_customer == "b_c":
            code_b = "01"
            code = "0211010"
        if self.partner_id.type_of_customer == "b_b":
            code_b = "02"
            code = "0111010"
        if self.move_type == "in_invoice":
            code = code_b+"00000"

        type_code = etree.SubElement(parent_node, ns["cbc"] + "InvoiceTypeCode",name=code)
        type_code.text = self._ubl_get_invoice_type_code()
        if self.narration:
            note = etree.SubElement(parent_node, ns["cbc"] + "Note")
            note.text = self.narration
        doc_currency = etree.SubElement(parent_node, ns["cbc"] + "DocumentCurrencyCode")
        doc_currency.text = self.currency_id.name
        tax_currency = etree.SubElement(parent_node, ns["cbc"] + "TaxCurrencyCode")
        tax_currency.text = self.currency_id.name
        if self.partner_id.type_of_customer == "b_b":
            line_count = etree.SubElement(parent_node, ns["cbc"] + "LineCountNumeric")
            line_count.text = str(len(self.invoice_line_ids))


    def _ubl_ext_header(self, parent_node, ns, version="2.1"):
        self.ensure_one()
        ext_test = etree.SubElement(
            parent_node, ns["ext"] + "UBLExtensions"
        )
        ext_test_n = etree.SubElement(ext_test, ns["ext"] + "UBLExtension")
        ext_test_n_node = etree.SubElement(ext_test_n, ns["ext"] + "ExtensionURI")
        ext_test_n_node.text = "Invoice Date :" + str(self.id) + " ;" + "Invoice Issue Date :" + str(self.invoice_date)


    def _ubl_get_invoice_type_code(self):
            if self.move_type == "out_invoice":
                return "380"
            elif self.move_type == "out_refund":
                return "381"
            elif self.move_type == "in_invoice":
                return "383"

    def _ubl_get_order_reference(self):
        """This method is designed to be inherited"""
        return self.invoice_origin

    def _ubl_add_order_reference(self, parent_node, ns, version="2.1"):
        self.ensure_one()
        sale_order_ref = self._ubl_get_order_reference()
        if sale_order_ref:
            order_ref = etree.SubElement(parent_node, ns["cac"] + "OrderReference")
            order_ref_id = etree.SubElement(order_ref, ns["cbc"] + "ID")
            order_ref_id.text = sale_order_ref

    def _ubl_get_contract_document_reference_dict(self):
        """Result: dict with key = Doc Type Code, value = ID"""
        self.ensure_one()
        return {}

    def _ubl_add_contract_document_reference(self, parent_node, ns, version="2.1"):
        self.ensure_one()
        cdr_dict = self._ubl_get_contract_document_reference_dict()
        for doc_type_code, doc_id in cdr_dict.items():
            cdr = etree.SubElement(parent_node, ns["cac"] + "ContractDocumentReference")
            cdr_id = etree.SubElement(cdr, ns["cbc"] + "ID")
            cdr_id.text = doc_id
            cdr_type_code = etree.SubElement(cdr, ns["cbc"] + "DocumentTypeCode")
            cdr_type_code.text = doc_type_code
    def new_additionalreference(self,parent_node, ns, version="2.1"):
        self.ensure_one()
        filename = "ICV"
        docu_reference = etree.SubElement(
            parent_node, ns["cac"] + "AdditionalDocumentReference"
        )
        docu_reference_id = etree.SubElement(docu_reference, ns["cbc"] + "ID")
        docu_reference_id.text = filename
        attach_node = etree.SubElement(docu_reference, ns["cac"] + "UUID")
        attach_node.text = str(self.name)
    def qr_code(self,parent_node, ns, version="2.1"):
        self.ensure_one()
        filename = "QR"
        docu_reference = etree.SubElement(
            parent_node, ns["cac"] + "AdditionalDocumentReference"
        )
        docu_reference_id = etree.SubElement(docu_reference, ns["cbc"] + "ID")
        docu_reference_id.text = filename
        attach_node = etree.SubElement(docu_reference, ns["cac"] + "Attachment")
        binary_node = etree.SubElement(
            attach_node,
            ns["cbc"] + "EmbeddedDocumentBinaryObject",
            mimeCode="text/plain"
        )
        ctx = dict()
        ctx["no_embedded_ubl_xml"] = True
        ctx["force_report_rendering"] = True
        binary_node.text = self.decoded_data
    def qr3_code(self,parent_node, ns, version="2.1"):
        filename = "ICV"
        docu_reference2 = etree.SubElement(
            parent_node, ns["cac"] + "MOUNIKAReference"
        )
        docu_reference_id_2 = etree.SubElement(docu_reference2, ns["cbc"] + "ID")
        docu_reference_id_2.text = filename
        attach1_node = etree.SubElement(docu_reference2, ns["cbc"] + "UUID")
        attach1_node.text = "70"

    #########off commented########################3
    # def qr_1code(self,parent_node, ns, version="2.1"):
    #     self.ensure_one()
    #     filename = "ICV"
    #     docu_reference = etree.SubElement(
    #         parent_node, ns["cac"] + "Mounika"
    #     )
    #     docu_reference_id = etree.SubElement(docu_reference, ns["cbc"] + "ID")
    #     docu_reference_id.text = filename
    #     attach1_node = etree.SubElement(docu_reference, ns["cbc"] + "UUID")
    #     attach1_node.text = "70"
        #####################################
    def qr_1code(self,parent_node, ns, version="2.1"):
        self.ensure_one()
        filename = "ICV"
        docu_reference = etree.SubElement(
            parent_node, ns["cac"] + "AdditionalDocumentReference"
        )
        docu_reference_id = etree.SubElement(docu_reference, ns["cbc"] + "ID")
        docu_reference_id.text = filename
        attach1_node = etree.SubElement(docu_reference, ns["cbc"] + "UUID")
        attach1_node.text = self.name
    def pih_code(self,parent_node, ns, version="2.1"):
        self.ensure_one()
        filename = "PIH"
        docu_reference = etree.SubElement(
            parent_node, ns["cac"] + "AdditionalDocumentReference"
        )
        docu_reference_id = etree.SubElement(docu_reference, ns["cbc"] + "ID")
        docu_reference_id.text = filename
        attach_nodes = etree.SubElement(docu_reference, ns["cac"] + "Attachment")
        binary_nodes = etree.SubElement(
            attach_nodes,
            ns["cbc"] + "EmbeddedDocumentBinaryObject",
            mimeCode="text/plain"
        )
       #we need to change"
        binary_nodes.text = "NWZlY2ViNjZmZmM4NmYzOGQ5NTI3ODZjNmQ2OTZjNzljMmRiYzIzOWRkNGU5MWI0NjcyOWQ3M2EyN2ZiNTdlOQ=="
    def billing_refence(self,parent_node, ns, version="2.1"):
        self.ensure_one()
        # filename = "QR"
        # if self.partner_id.type_of_customer == "b_c":
        docu_reference = etree.SubElement(
            parent_node, ns["cac"] + "BillingReference"
        )
        docu_reference_ids = etree.SubElement(docu_reference, ns["cac"] + "InvoiceDocumentReference")
        binary_node = etree.SubElement(docu_reference_ids, ns["cbc"] + "ID")
        # docu_reference_id.text = self.name
        # attach_node = etree.SubElement(docu_reference, ns["cac"] + "Attachment")
        # binary_node = etree.SubElement(
        #     attach_node,
        #     ns["cbc"] + "EmbeddedDocumentBinaryObject",
        #     mimeCode="text/plain"
        # )
        ctx = dict()
        ctx["no_embedded_ubl_xml"] = True
        ctx["force_report_rendering"] = True
        binary_node.text = "Invoice Date :"+str(self.id)+" ;"+"Invoice Issue Date :"+str(self.invoice_date)

    def signature_refence(self,parent_node, ns, version="2.1"):
        self.ensure_one()
        # cdr = etree.SubElement(parent_node, ns["cac"] + "Signature")
        # cdr_id = etree.SubElement(cdr, ns["cbc"] + "ID")
        # cdr_id.text = 'urn:oasis:names:specification:ubl:signature:Invoice'
        # cdr_type_code = etree.SubElement(cdr, ns["cbc"] + "SignatureMethod")
        # cdr_type_code.text = "urn:oasis:names:specification:ubl:dsig:enveloped:xades"
        pay_means = etree.SubElement(parent_node, ns["cac"] + "Signature")
        pay_means_code = etree.SubElement(
        pay_means, ns["cbc"] + "ID")
        pay_means_code.text = "urn:oasis:names:specification:ubl:signature:Invoice"
        pay_due_date = etree.SubElement(pay_means, ns["cbc"] + "SignatureMethod")
        pay_due_date.text = "urn:oasis:names:specification:ubl:dsig:enveloped:xades"

    def _ubl_add_attachments(self, parent_node, ns, version="2.1"):
        self.ensure_one()
        self.billing_refence(parent_node, ns, version="2.1")
        # if self.decoded_data:
        self.testing()
        self.qr_code(parent_node, ns, version="2.1")
        self.qr_1code(parent_node, ns, version="2.1")
        self.pih_code(parent_node, ns, version="2.1")

        # self.signature_refence(parent_node, ns, version="2.1")
        # if self.company_id.embed_pdf_in_ubl_xml_invoice and not self.env.context.get(
        #     "no_embedded_pdf"
        # ):
        # self.signature_refence(parent_node, ns, version="2.1")
        filename = "Invoice-" + self.name + ".pdf"
        docu_reference = etree.SubElement(
            parent_node, ns["cac"] + "AdditionalDocumentReference"
        )
        docu_reference_id = etree.SubElement(docu_reference, ns["cbc"] + "ID")
        docu_reference_id.text = filename
        attach_node = etree.SubElement(docu_reference, ns["cac"] + "Attachment")
        binary_node = etree.SubElement(
            attach_node,
            ns["cbc"] + "EmbeddedDocumentBinaryObject",
            mimeCode="application/pdf",
            filename=filename,
        )
        ctx = dict()
        ctx["no_embedded_ubl_xml"] = True
        ctx["force_report_rendering"] = True
        # pdf_inv = (
        #     self.with_context(ctx)
        #     .env.ref("account.account_invoices")
        #     ._render_qweb_pdf(self.ids)[0]
        # )
        ########changed########################
        pdf_inv = self.with_context(ctx).env.ref(
            'account_invoice_ubl.account_invoices_1')._render_qweb_pdf(self.ids)[0]
        pdf_inv = self.with_context(ctx).env.ref(
            'account_invoice_ubl.account_invoices_b2b')._render_qweb_pdf(self.ids)[0]
        pdf_inv = self.with_context(ctx).env.ref(
            'account_invoice_ubl.account_invoices_b2b_credit')._render_qweb_pdf(self.ids)[0]
        # pdf_inv = self.with_context(ctx).env.ref(
        #     'account_invoice_ubl.account_invoices_b2b_debit')._render_qweb_pdf(self.ids)[0]
        pdf_inv = self.with_context(ctx).env.ref(
            'account_invoice_ubl.account_invoices_b2c')._render_qweb_pdf(self.ids)[0]
        pdf_inv = self.with_context(ctx).env.ref(
                    'account_invoice_ubl.account_invoices_b2c_credit')._render_qweb_pdf(self.ids)[0]
        # pdf_inv = self.with_context(ctx).env.ref(
        #                 'account_invoice_ubl.account_invoices_b2c_debit')._render_qweb_pdf(self.ids)[0]
        # pdf_inv = self.with_context(ctx).env.ref(
        #     'jasaraeinvoice.minister_invoice_report_1')._render_qweb_pdf(self.ids)[0]
        # pdf_inv = self.with_context(ctx).env.ref(
        #     'masar_arabia_einvoice.masar_arabic_einvoice_report_1')._render_qweb_pdf(self.ids)[0]
        # pdf_inv = self.with_context(ctx).env.ref(
        #     'galvanization_report.galvanization_invoice_report')._render_qweb_pdf(self.ids)[0]
        binary_node.text = base64.b64encode(pdf_inv)
        # self.qr3_code(parent_node, ns, version="2.1")


        # filename = "ICV"
        # icv_reference = etree.SubElement(
        #     parent_node, ns["cac"] + "AdditionalDocumentReference"
        # )
        # icv_reference_id = etree.SubElement(icv_reference, ns["cbc"] + "ID")
        # icv_reference_id.text = filename
        # icv_reference_node = etree.SubElement(icv_reference, ns["cac"] + "UUID")
        # icv_reference_node.text = self.name



    def _ubl_add_legal_monetary_total(self, parent_node, ns, version="2.1"):
        self.ensure_one()
        monetary_total = etree.SubElement(parent_node, ns["cac"] + "LegalMonetaryTotal")
        cur_name = self.currency_id.name
        prec = self.currency_id.decimal_places
        line_total = etree.SubElement(
            monetary_total, ns["cbc"] + "LineExtensionAmount", currencyID=cur_name
        )
        line_total.text = "%0.*f" % (prec, self.amount_untaxed)
        tax_excl_total = etree.SubElement(
            monetary_total, ns["cbc"] + "TaxExclusiveAmount", currencyID=cur_name
        )
        tax_excl_total.text = "%0.*f" % (prec, self.amount_untaxed)
        tax_incl_total = etree.SubElement(
            monetary_total, ns["cbc"] + "TaxInclusiveAmount", currencyID=cur_name
        )
        tax_incl_total.text = "%0.*f" % (prec, self.amount_total)
        prepaid_amount = etree.SubElement(
            monetary_total, ns["cbc"] + "PrepaidAmount", currencyID=cur_name
        )
        prepaid_value = self.amount_total - self.amount_residual
        prepaid_amount.text = "%0.*f" % (prec, prepaid_value)
        payable_amount = etree.SubElement(
            monetary_total, ns["cbc"] + "PayableAmount", currencyID=cur_name
        )
        payable_amount.text = "%0.*f" % (prec, self.amount_residual)

    def _ubl_add_invoice_line(self, parent_node, iline, line_number, ns, version="2.1"):
        self.ensure_one()
        cur_name = self.currency_id.name
        line_root = etree.SubElement(parent_node, ns["cac"] + "InvoiceLine")
        dpo = self.env["decimal.precision"]
        qty_precision = dpo.precision_get("Product Unit of Measure")
        price_precision = dpo.precision_get("Product Price")
        account_precision = self.currency_id.decimal_places
        line_id = etree.SubElement(line_root, ns["cbc"] + "ID")
        line_id.text = str(line_number)
        uom_unece_code = False
        # product_uom_id is not a required field on account.move.line
        if iline.product_uom_id.unece_code:
            uom_unece_code = iline.product_uom_id.unece_code
            quantity = etree.SubElement(
                line_root, ns["cbc"] + "InvoicedQuantity", unitCode=uom_unece_code
            )
        else:
            quantity = etree.SubElement(line_root, ns["cbc"] + "InvoicedQuantity")
        qty = iline.quantity
        quantity.text = "%0.*f" % (qty_precision, qty)
        line_amount = etree.SubElement(
            line_root, ns["cbc"] + "LineExtensionAmount", currencyID=cur_name
        )
        line_amount.text = "%0.*f" % (account_precision, iline.price_subtotal)
        self._ubl_add_invoice_line_tax_total(iline, line_root, ns, version=version)
        self._ubl_add_item(
            iline.name,iline, iline.product_id, line_root, ns, type_="sale", version=version
        )
        price_node = etree.SubElement(line_root, ns["cac"] + "Price")
        price_amount = etree.SubElement(
            price_node, ns["cbc"] + "PriceAmount", currencyID=cur_name
        )
        price_unit = 0.0
        # Use price_subtotal/qty to compute price_unit to be sure
        # to get a *tax_excluded* price unit
        if not float_is_zero(qty, precision_digits=qty_precision):
            price_unit = float_round(
                iline.price_subtotal / float(qty), precision_digits=price_precision
            )
        price_amount.text = "%0.*f" % (price_precision, price_unit)
        if uom_unece_code:
            base_qty = etree.SubElement(
                price_node, ns["cbc"] + "BaseQuantity", unitCode=uom_unece_code
            )
        else:
            base_qty = etree.SubElement(price_node, ns["cbc"] + "BaseQuantity")
        base_qty.text = "%0.*f" % (qty_precision, qty)

    def _ubl_add_invoice_line_tax_total(self, iline, parent_node, ns, version="2.1"):
        self.ensure_one()
        cur_name = self.currency_id.name
        prec = self.currency_id.decimal_places
        tax_total_node = etree.SubElement(parent_node, ns["cac"] + "TaxTotal")
        price = iline.price_unit * (1 - (iline.discount or 0.0) / 100.0)
        res_taxes = iline.tax_ids.compute_all(
            price,
            quantity=iline.quantity,
            product=iline.product_id,
            partner=self.partner_id,
        )
        tax_total = float_round(
            res_taxes["total_included"] - res_taxes["total_excluded"],
            precision_digits=prec,
        )
        tax_amount_node = etree.SubElement(
            tax_total_node, ns["cbc"] + "TaxAmount", currencyID=cur_name
        )
        tax_amount_node.text = "%0.*f" % (prec, tax_total)
        #####################################################code added#######################
        rounding_amount_node = etree.SubElement(
            tax_total_node, ns["cbc"] + "RoundingAmount", currencyID=cur_name
        )
        actual = (iline.quantity * iline.price_unit)-iline.discount
        rounding_amount = actual * sum(iline.tax_ids.mapped('amount')) / 100
        rounding_amounts = actual+rounding_amount

        rounding_amount_node.text = "%0.*f" % (prec, rounding_amounts)
        ##########################################################33

        if not float_is_zero(tax_total, precision_digits=prec):
            for res_tax in res_taxes["taxes"]:
                tax = self.env["account.tax"].browse(res_tax["id"])
                # we don't have the base amount in res_tax :-(
                self._ubl_add_tax_subtotal(
                    False,
                    res_tax["amount"],
                    tax,
                    cur_name,
                    tax_total_node,
                    ns,
                    version=version,
                )

    def _ubl_add_tax_total(self, xml_root, ns, version="2.1"):
        self.ensure_one()
        cur_name = self.currency_id.name
        tax_total_node = etree.SubElement(xml_root, ns["cac"] + "TaxTotal")
        tax_amount_node = etree.SubElement(
            tax_total_node, ns["cbc"] + "TaxAmount", currencyID=cur_name
        )
        prec = self.currency_id.decimal_places
        tax_amount_node.text = "%0.*f" % (prec, self.amount_tax)
        if not float_is_zero(self.amount_tax, precision_digits=prec):
            tax_lines = self.line_ids.filtered(lambda line: line.tax_line_id)
            res = {}
            # There are as many tax line as there are repartition lines
            done_taxes = set()
            for line in tax_lines:
                res.setdefault(
                    line.tax_line_id.tax_group_id,
                    {"base": 0.0, "amount": 0.0, "tax": False},
                )
                res[line.tax_line_id.tax_group_id]["amount"] += line.price_subtotal
                tax_key_add_base = tuple(self._get_tax_key_for_group_add_base(line))
                if tax_key_add_base not in done_taxes:
                    res[line.tax_line_id.tax_group_id]["base"] += line.tax_base_amount
                    res[line.tax_line_id.tax_group_id]["tax"] = line.tax_line_id
                    done_taxes.add(tax_key_add_base)
            res = sorted(res.items(), key=lambda l: l[0].sequence)
            for _group, amounts in res:
                self._ubl_add_tax_subtotal(
                    amounts["base"],
                    amounts["amount"],
                    amounts["tax"],
                    cur_name,
                    tax_total_node,
                    ns,
                    version=version,
                )

    def generate_invoice_ubl_xml_etree(self, version="2.1"):
        self.ensure_one()
        nsmap, ns = self._ubl_get_nsmap_namespace("Invoice-2", version=version)
        xml_root = etree.Element("Invoice", nsmap=nsmap)
        # import
        ublextensions = etree.SubElement(xml_root, f"{ns['ext']}UBLExtensions")
        ublextension = etree.SubElement(ublextensions, f"{ns['ext']}UBLExtension")
        ublextensionURI = etree.SubElement(ublextension, f"{ns['ext']}ExtensionURI")
        ublextensionURI.text = "urn:oasis:names:specification:ubl:dsig:enveloped:xades"
        extcontent = etree.SubElement(ublextension, f"{ns['ext']}ExtensionContent")
        # extcontent_id = etree.SubElement(extcontent, f"{ns['sig']}UBLDocumentSignatures",{"xmlns:sac='urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2',xmlns:sbc='urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2', xmlns:sig='urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2'"})

        # extcontents = etree.SubElement(extcontent, f"{ns['ext']}UBLExtensions|ext:UBLExtension|ext:ExtensionContent|sig:UBLDocumentSignatures|sac:SignatureInformation")
        # nsmaps = self._ubl_get_sign_namespace("Sign", version=version)
        # xml_rootss = etree.SubElement(ublextension, nsmap=nsmaps)

        # extcontents = etree.SubElement(extcontent, f"{ns['sig']}UBLDocumentSignatures")
        # etree.SubElement(extcontent, f"{ns['sig']}UBLDocumentSignatures")
        # import xades
        # import xmlsig

        # nsmap_test = {
        #     "sac": "urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2",
        #     "sbc": "urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2",
        #     "sig": "urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2"
        # }
        # NSMAP = {None: "XMLNamespaces.empty", 'sac': "urn:oasis:names:specification:ubl:schema:xsd:SignatureAggregateComponents-2",
        #          'sbc': "urn:oasis:names:specification:ubl:schema:xsd:SignatureBasicComponents-2",
        #          'sig': "urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2"}


        ubl_doc = etree.SubElement(extcontent, f"{ns['sig']}UBLDocumentSignatures")
        addinfos = etree.SubElement(ubl_doc, f"{ns['sac']}SignatureInformation")
        addinf_id = etree.SubElement(addinfos, f"{ns['cbc']}ID")
        addinf_id.text = "urn:oasis:names:specification:ubl:signature:1"
        addinfo_ref = etree.SubElement(addinfos, f"{ns['sbc']}ReferencedSignatureID")
        addinfo_ref.text ="urn:oasis:names:specification:ubl:signature:Invoicesadas"

        ad_sign = etree.SubElement(addinfos, f"{ns['ds']}Signature",Id="signature")
        ad_sign_info = etree.SubElement(ad_sign, f"{ns['ds']}SignedInfo")
        ############################################################################3
        # ad_sign_cano= etree.SubElement(ad_sign_info, f"{ns['ds']}CanonicalizationMethod",Algorithm = "http://www.w3.org/2001/10/xml-exc-c14n#")
        # ad_sign_method= etree.SubElement(ad_sign_info, f"{ns['ds']}SignatureMethod",Algorithm = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256")
        # ad_sign_ref= etree.SubElement(ad_sign_info, f"{ns['ds']}Reference",URI = "")
        #
        #
        # ad_sign_trans= etree.SubElement(ad_sign_ref, f"{ns['ds']}Transforms")
        # ad_sign_transm= etree.SubElement(ad_sign_trans, f"{ns['ds']}Transform",Algorithm = "http://www.w3.org/2002/06/xmldsig-filter2")
        # ad_sign_transm.text = "xmlns =http://www.w3.org/2002/06/xmldsig-filter2"
        # ad_sign_diag= etree.SubElement(ad_sign_ref, f"{ns['ds']}DigestMethod",Algorithm = "http://www.w3.org/2001/04/xmlenc#sha256")
        # ad_sign_diag.text = "ad_sign_diag"
        # ad_sign_diag_val= etree.SubElement(ad_sign_ref, f"{ns['ds']}DigestValue")
        # ad_sign_diag_val.text = "g6h8KnGd + Y4DCdnGk5oIUbBwjJB3MMGlyizaFyCqH7I = "
        # ad_sign_ref1= etree.SubElement(ad_sign_info, f"{ns['ds']}Reference",Id = "reference-signedpropeties",Type = "http://uri.etsi.org/01903#SignedProperties",URI = "#SignedProperties_1")
        # ad_sign_dige1= etree.SubElement(ad_sign_ref1, f"{ns['ds']}DigestMethod",Algorithm = "http://www.w3.org/2001/04/xmlenc#sha256")
        # ad_sign_dige_val1= etree.SubElement(ad_sign_ref1, f"{ns['ds']}DigestValue")
        # ad_sign_ref2= etree.SubElement(ad_sign_info, f"{ns['ds']}Reference",Id = "reference-keyinfo",Type = "http://uri.etsi.org/01903#SignedProperties",URI = "#SignedProperties_1")
        # ad_sign_dige2= etree.SubElement(ad_sign_ref2, f"{ns['ds']}DigestMethod",Algorithm = "#KeyInfoId")
        # ad_sign_dige_val1= etree.SubElement(ad_sign_ref2, f"{ns['ds']}DigestValue")
        # ad_sign_dige_val1.text = "BaZyFTXyxM8aIJhtiemem1lEwKR75ksXb33lsMqD89w ="
        #
        #
        #
        # # add_Reference = etree.SubElement(ad_sign_info, f"{ns['ds']}Reference")
        # # add_digest = etree.SubElement(add_Reference, f"{ns['ds']}DigestMethod",Algorithm = "http://www.w3.org/2001/04/xmlenc#sha256")
        # # add_digestvalue = etree.SubElement(add_Reference, f"{ns['ds']}DigestValue")
        # signature_value = etree.SubElement(ad_sign_info, f"{ns['ds']}SignatureValue",Id = "SignatureValue1")
        #
        # signature_value.text = "Z8 / Kt / ZF / syaHxYr6 / qoTz + nTJe3IV1m9Hj3WPOl1CZ / p5intUORW0IinpMum4rvPkLYpKPVbi39WCJujEqVOVFw5xezZlwmrRghmUeyTyKazK7mKEEMXCad + FGCZj2Gz1nkqi5aNyNX / lN7m9Ix7rZ8"
        #
        #



        # ad_sign_infovalue = etree.SubElement(ad_sign_info, f"{ns['ds']}SignatureValue")
        ############################################################################3

        canonical = etree.SubElement(ad_sign_info, f"{ns['ds']}CanonicalizationMethod",Algorithm="http://www.w3.org/2006/12/xml-c14n11")
        sign_method = etree.SubElement(ad_sign_info, f"{ns['ds']}SignatureMethod",Algorithm="http://www.w3.org/2001/04/xmldsig-more#ecdsa-sha256")
        # reference = etree.SubElement(ad_sign_info, f"{ns['ds']}Reference",URI="UBL-Invoice-2.0-Detached.xml")
        # digest_method = etree.SubElement(reference, f"{ns['ds']}DigestMethod",Algorithm="http://www.w3.org/2000/09/xmldsig#sha1")
        # digest_value = etree.SubElement(reference, f"{ns['ds']}DigestValue")
        # digest_value.text = "qM/+Gsg4/E/0p3fE9LTZA6Xtkds="

        reference = etree.SubElement(ad_sign_info, f"{ns['ds']}Reference",Id="invoiceSignedData",URI="")
        transforms = etree.SubElement(reference, f"{ns['ds']}Transforms")
        transforms_sub1 = etree.SubElement(transforms, f"{ns['ds']}Transform",Algorithm="http://www.w3.org/2006/12/xml-c14n11")
        transform_sub2 = etree.SubElement(transforms, f"{ns['ds']}Transform",Algorithm="http://www.w3.org/2000/09/xmldsig#enveloped-signature")
        transform_sub3 = etree.SubElement(transforms, f"{ns['ds']}Transform",Algorithm="http://www.w3.org/TR/1999/REC-xpath-19991116")
        transforms2 = etree.SubElement(transform_sub3, f"{ns['ds']}XPath",)
        transforms2.text = "not(ancestor-or-self::ds:Signature)"
        digest_method3 = etree.SubElement(reference, f"{ns['ds']}DigestMethod",Algorithm="http://www.w3.org/2001/04/xmlenc#sha256")
        digest_value3 = etree.SubElement(reference, f"{ns['ds']}DigestValue")
        digest_value3.text = "zMwFW6o9UQACVwThiFAEeDl9mNYAk+fS4kYsM4uqlQM="

        reference2 = etree.SubElement(ad_sign_info, f"{ns['ds']}Reference",Type = "http://www.w3.org/2000/09/xmldsig#SignatureProperties", URI = "#xadesSignedProperties")
        digest_method2 = etree.SubElement(reference2, f"{ns['ds']}DigestMethod", Algorithm="http://www.w3.org/2001/04/xmlenc#sha256")
        digest_value2 = etree.SubElement(reference2, f"{ns['ds']}DigestValue")
        digest_value2.text = "hZFPNOk4TgvIWqYzekIaYageKq1phW4rdATemEi+1s8="













        # reference2 = etree.SubElement(ad_sign_info, f"{ns['ds']}Reference", URI="#xades-test-s")
        # digest_method2 = etree.SubElement(reference2, f"{ns['ds']}DigestMethod",Algorithm="http://www.w3.org/2000/09/xmldsig#sha1")
        # digest_value2 = etree.SubElement(reference2, f"{ns['ds']}DigestValue")
        # digest_value2.text = "mjiR61tL2dV3HMus3GBG/aEjbt4="



        ######next##########################
        ad_sign_value = etree.SubElement(ad_sign, f"{ns['ds']}SignatureValue")
        ad_sign_value.text = "+W2BZpNe+ZbX+Rvbeww4gUz3kbGzlHGD8ZcUrnYUlxcA5kicOwPOJ5pBzjRLaDWP69FyY/vsGWvPHH3jZJAt9g=="
        ad_key_info = etree.SubElement(ad_sign, f"{ns['ds']}KeyInfo")
        x509Data = etree.SubElement(ad_key_info, f"{ns['ds']}X509Data")
        x509Certificate = etree.SubElement(x509Data, f"{ns['ds']}X509Certificate")
        x509Certificate.text = "MIIBmzCCAUECCQDQROomkk8YkDAKBggqhkjOPQQDAjBWMQswCQYDVQQGEwJQTDEQMA4GA1UECAwHU2lsZXNpYTERMA8GA1UEBwwIS2F0b3dpY2UxDTALBgNVBAoMBEdBWlQxEzARBgNVBAMMCkNvbW1vbk5hbWUwIBcNMjEwOTA2MTgwOTA1WhgPNDQ4NTEwMTgxODA5MDVaMFYxCzAJBgNVBAYTAlBMMRAwDgYDVQQIDAdTaWxlc2lhMREwDwYDVQQHDAhLYXRvd2ljZTENMAsGA1UECgwER0FaVDETMBEGA1UEAwwKQ29tbW9uTmFtZTBWMBAGByqGSM49AgEGBSuBBAAKA0IABJboxJQD/AlFyPQCWM3S2ekwGnkhKpOnyP+tjsLYFcJfLLTdX+U/uOfQtKAm/KRXI1E9d8DjOOkVFo5Q1ZQE25QwCgYIKoZIzj0EAwIDSAAwRQIhANULHFfKoroAMgdoUQJ/UwjhD3xHgMeAXjgVpZftENoYAiB7WFgx0hLuJTJbLpYCzpzdpWVOXrIr8g4XvtWKl02j1w=="
        ########adding objects###############

        object = etree.SubElement(ad_sign, f"{ns['ds']}Object")
        qualifying_properties = etree.SubElement(object, f"{ns['xades']}QualifyingProperties", Target="signature")
        signed_properties = etree.SubElement(qualifying_properties, f"{ns['xades']}SignedProperties",Id="xadesSignedProperties" )
        signed_sign_property= etree.SubElement(signed_properties, f"{ns['xades']}SignedSignatureProperties")
        signed_time = etree.SubElement(signed_sign_property, f"{ns['xades']}SigningTime")
        signed_time.text = "2021-11-18T06:50:54Z"
        signed_certificate = etree.SubElement(signed_sign_property, f"{ns['xades']}SigningCertificate")
        cert = etree.SubElement(signed_certificate, f"{ns['xades']}Cert")
        cert_digest = etree.SubElement(cert, f"{ns['xades']}CertDigest")
        digest_method3 = etree.SubElement(cert_digest, f"{ns['ds']}DigestMethod",Algorithm="http://www.w3.org/2001/04/xmlenc#sha256")
        digest_value3 = etree.SubElement(cert_digest, f"{ns['ds']}DigestValue")
        digest_value3.text = "nvbAuQrmCYaLthR3Lh1TdUZO0aF5Pe11H+seNBSYD3w="
        issuer_serial = etree.SubElement(cert, f"{ns['xades']}IssuerSerial")
        x_issuerName = etree.SubElement(issuer_serial, f"{ns['ds']}X509IssuerName")
        x_issuerName.text = "CN=CommonName, O=GAZT, L=Katowice, ST=Silesia, C=PL"
        x_serial_number = etree.SubElement(issuer_serial, f"{ns['ds']}X509SerialNumber")
        x_serial_number.text = "15007377309689649296"


























        # ad_key_value = etree.SubElement(ad_key_info, f"{ns['ds']}KeyValue")
        # rsa_key_value= etree.SubElement(ad_key_value, f"{ns['ds']}RSAKeyValue")
        # modulus = etree.SubElement(rsa_key_value, f"{ns['ds']}Modulus")
        # modulus.text = "MIIBmzCCAUECCQDQROomkk8YkDAKBggqhkjOPQQDAjBWMQswCQYDVQQGEwJQTDEQMA4GA1UECAwHU2lsZXNpYTERMA8GA1UEBwwIS2F0b3dpY2UxDTALBgNVBAoMBEdBWlQxEzARBgNVBAMMCkNvbW1vbk5hbWUwIBcNMjEwOTA2MTgwOTA1WhgPNDQ4NTEwMTgxODA5MDVaMFYxCzAJBgNVBAYTAlBMMRAwDgYDVQQIDAdTaWxlc2lhMREwDwYDVQQHDAhLYXRvd2ljZTENMAsGA1UECgwER0FaVDETMBEGA1UEAwwKQ29tbW9uTmFtZTBWMBAGByqGSM49AgEGBSuBBAAKA0IABJboxJQD/AlFyPQCWM3S2ekwGnkhKpOnyP+tjsLYFcJfLLTdX+U/uOfQtKAm/KRXI1E9d8DjOOkVFo5Q1ZQE25QwCgYIKoZIzj0EAwIDSAAwRQIhANULHFfKoroAMgdoUQJ/UwjhD3xHgMeAXjgVpZftENoYAiB7WFgx0hLuJTJbLpYCzpzdpWVOXrIr8g4XvtWKl02j1w=="
        # exponent = etree.SubElement(rsa_key_value, f"{ns['ds']}Exponent")
        # exponent.text = "AQAB"
        # # x509Data = etree.SubElement(ad_key_value, f"{ns['ds']}X509Data")
        # # x509certificate = etree.SubElement(x509Data, f"{ns['ds']}X509Certificate")
        # # x509certificate.text = "MIICcTCCAdoCCQDzGe/d5rwBKzANBgkqhkiG9w0BAQUFADB9MQswCQYDVQQGEwJVUzEWMBQGA1UECAwNTWFzc2FjaHVzZXR0czETMBEGA1UEBwwKQnVybGluZ3RvbjEOMAwGA1UECgwFT0FTSVMxIDAeBgNVBAsMF1VCTCBUZWNobmljYWwgQ29tbWl0dGVlMQ8wDQYDVQQDDAZVQkwgVEMwHhcNMTMwMjE1MTg1OTQ2WhcNMTMwMzE3MTg1OTQ2WjB9MQswCQYDVQQGEwJVUzEWMBQGA1UECAwNTWFzc2FjaHVzZXR0czETMBEGA1UEBwwKQnVybGluZ3RvbjEOMAwGA1UECgwFT0FTSVMxIDAeBgNVBAsMF1VCTCBUZWNobmljYWwgQ29tbWl0dGVlMQ8wDQYDVQQDDAZVQkwgVEMwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBALlxJoNMk2TdWH+yLsA3H/jIR4yC3D7RV1VtxURacucplgw5qDnXTyaxt0usx3Am7pHaiUfnyB4aRmrjIn02wuJPRdFDYE9A0s8aDpFTBcL/6URCtvJb5w2Q9axp0vRirXMjjFWxnuQUpePYgSOcYaVLZkWMVUf0QMUlJgq32RaDAgMBAAEwDQYJKoZIhvcNAQEFBQADgYEAVtqeUFJQa64pqCYJAxflCGdOKFBX2p8LCo3KeupnQC9UvLdOxuS8fAjzo40FQG687/7NGcZ30ysVjy/s3XyqxDFLln601vI470i96Gip3cBF8WHB5lUnvaT9dNEYFDBBR22glEnY9SA8y8EbbO+Cy8hIQEzULoVOkr/aJfeH5w4="
        # # x509subject = etree.SubElement(x509Data, f"{ns['ds']}X509SubjectName")
        # # x509subject.text = "CN=UBL TC,OU=UBL Technical Committee,O=OASIS,L=Burlington,ST=Massachusetts,C=US"
        # # x509issueName = etree.SubElement(x509Data, f"{ns['ds']}X509IssuerName")
        # # x509issueName.text = "CN=UBL TC,OU=UBL Technical Committee,O=OASIS,L=Burlington,ST=Massachusetts,C=US"
        # # x509serialnumber = etree.SubElement(x509Data, f"{ns['ds']}X509SerialNumber")
        # # x509serialnumber.text = "17517295961972146475"
        #









        # ad_sign_method.text="6575676576575"

        # nsmaps, nss = self._ubl_get_sign_namespace("ExtensionContent", version=version)
        # xml_root = etree.Element("Sign", nsmap=nsmaps)
        # extcontentest = etree.SubElement(extcontent, nsmap=nsmaps)



        self._ubl_add_header(xml_root, ns, version=version)




        # self._ubl_ext_header(xml_root, ns, version=version)
        # self.new_additionalreference(xml_root, ns, version="2.1")
        self._ubl_add_order_reference(xml_root, ns, version=version)
        # self.uuid_refence(xml_root, ns, version="2.1")
        self._ubl_add_contract_document_reference(xml_root, ns, version=version)
        self._ubl_add_attachments(xml_root, ns, version=version)
        self.signature_refence(xml_root, ns, version="2.1")
        self._ubl_add_supplier_party(
            False,
            self.company_id,
            "AccountingSupplierParty",
            xml_root,
            ns,
            version=version,
        )

        self._ubl_add_customer_party(
            self.partner_id,
            False,
            "AccountingCustomerParty",
            xml_root,
            ns,
            version=version,
        )
        # the field 'partner_shipping_id' is defined in the 'sale' module
        if hasattr(self, "partner_shipping_id") and self.partner_shipping_id:
            self._ubl_add_delivery(self.partner_shipping_id, xml_root, ns)
        # Put paymentmeans block even when invoice is paid ?
        payment_identifier = self.get_payment_identifier()
        self._ubl_add_payment_means(
            self.partner_bank_id,
            self.payment_mode_id,
            self.invoice_date_due,
            xml_root,
            ns,
            payment_identifier=payment_identifier,
            version=version,
        )
        if self.invoice_payment_term_id:
            self._ubl_add_payment_terms(
                self.invoice_payment_term_id, xml_root, ns, version=version
            )
        self._ubl_add_tax_total(xml_root, ns, version=version)
        self.ensure_one()
        cur_name = self.currency_id.name
        #########code adding#############3
        tax_total_node = etree.SubElement(xml_root, ns["cac"] + "TaxTotal")
        tax_amount_nodes = etree.SubElement(
            tax_total_node, ns["cbc"] + "TaxAmount", currencyID=cur_name
        )
        prec = self.currency_id.decimal_places
        tax_amount_nodes.text = "%0.*f" % (prec, self.amount_tax)

        self._ubl_add_legal_monetary_total(xml_root, ns, version=version)

        line_number = 0
        for iline in self.invoice_line_ids:
            line_number += 1
            self._ubl_add_invoice_line(
                xml_root, iline, line_number, ns, version=version
            )
        return xml_root

    def generate_ubl_xml_string(self, version="2.1"):
        self.ensure_one()
        assert self.state == "posted"
        # assert self.move_type in ("out_invoice", "out_refund","in_invoice")
        assert self.move_type in ("out_invoice", "out_refund","in_invoice","in_refund")
        logger.debug("Starting to generate UBL XML Invoice file")
        lang = self.get_ubl_lang()
        # The aim of injecting lang in context
        # is to have the content of the XML in the partner's lang
        # but the problem is that the error messages will also be in
        # that lang. But the error messages should almost never
        # happen except the first days of use, so it's probably
        # not worth the additional code to handle the 2 langs
        xml_root = self.with_context(lang=lang).generate_invoice_ubl_xml_etree(
            version=version
        )
        xml_string = etree.tostring(
            xml_root, pretty_print=True, encoding="UTF-8", xml_declaration=True
        )
        self._ubl_check_xml_schema(xml_string, "Invoice", version=version)
        logger.debug(
            "Invoice UBL XML file generated for account invoice ID %d " "(state %s)",
            self.id,
            self.state,
        )
        logger.debug(xml_string.decode("utf-8"))
        return xml_string

    def get_ubl_filename(self, version="2.1"):
        """This method is designed to be inherited"""
        return "UBL-Invoice-%s.xml" % version

    def get_ubl_version(self):
        return self.env.context.get("ubl_version") or "2.1"

    def get_ubl_lang(self):
        self.ensure_one()
        return self.partner_id.lang or "en_US"

    def add_xml_in_pdf_buffer(self, buffer):
        self.ensure_one()
        if self.is_ubl_sale_invoice_posted():
            version = self.get_ubl_version()
            xml_filename = self.get_ubl_filename(version=version)
            xml_string = self.generate_ubl_xml_string(version=version)
            buffer = self._ubl_add_xml_in_pdf_buffer(xml_string, xml_filename, buffer)
        return buffer

    def embed_ubl_xml_in_pdf(self, pdf_content):
        self.ensure_one()
        if self.is_ubl_sale_invoice_posted():
            version = self.get_ubl_version()
            xml_filename = self.get_ubl_filename(version=version)
            xml_string = self.generate_ubl_xml_string(version=version)
            pdf_content = self.embed_xml_in_pdf(
                xml_string, xml_filename, pdf_content=pdf_content
            )
        return pdf_content

    def attach_ubl_xml_file_button(self):
        self.ensure_one()
        if self.move_type in ('out_invoice','out_refund','in_refund'):
            assert self.move_type in ("out_invoice", "out_refund","in_invoice","in_refund")

            assert self.state == "posted"
            version = self.get_ubl_version()
            xml_string = self.generate_ubl_xml_string(version=version)
            filename = self.get_ubl_filename(version=version)
            attach = (
                self.env["ir.attachment"]
                .with_context({})
                .create(
                    {
                        "name": filename,
                        "res_id": self.id,
                        "res_model": self._name,
                        "datas": base64.b64encode(xml_string),
                        # If default_type = 'out_invoice' in context, 'type'
                        # would take 'out_invoice' value by default !
                        "type": "binary",
                    }
                )
            )
            action = self.env["ir.attachment"].action_get()
            action.update({"res_id": attach.id, "views": False, "view_mode": "form,tree"})
            return action

    def is_ubl_sale_invoice_posted(self):
        self.ensure_one()
        is_ubl = self.company_id.xml_format_in_pdf_invoice == "ubl"
        if self.move_type == 'out_invoice':
            if is_ubl and self.is_sale_document() and self.state == "posted":
                return True
        else:
            if self.move_type == 'in_invoice':
                if is_ubl and self.is_purchase_document() and self.state == "posted":
                    return True

        return False


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

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
    ], string='VAT CATEGORY',default="S")
