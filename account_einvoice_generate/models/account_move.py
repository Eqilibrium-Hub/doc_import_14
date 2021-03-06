# Copyright 2018-2020 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_payment_identifier(self):
        """This method is designed to be inherited in localization modules"""
        self.ensure_one()
        return None

    @api.model
    def _get_invoice_report_names(self):
        return [
            "account.report_invoice",
            "account.report_invoice_with_payments",
            "account_invoice_ubl.report_invoice_1",
            "account_invoice_ubl.report_invoice_b2b",
            "account_invoice_ubl.report_invoice_b2b_credit",
            # "account_invoice_ubl.report_invoice_b2b_debit",
            "account_invoice_ubl.report_invoice_b2c",
            "account_invoice_ubl.report_invoice_b2c_credit",
            # "account_invoice_ubl.report_invoice_b2c_debit",
            # "jasaraeinvoice.minister_invoice_report_1"
            # "masar_arabia_einvoice.masar_arabic_einvoice_report_1",
            # "galvanization_report.galvanization_invoice_report",
        ]

    def _xml_format_in_pdf_invoice(self):
        """Returns the format if it is possible to generate the XML
        Otherwize return False"""
        self.ensure_one()
        xml_format = self.company_id.xml_format_in_pdf_invoice
        # I want to allow embedded XML even on draft invoice
        # So I write here the conditions to be able to generate a valid XML
        if (
            xml_format
            and xml_format != "none"
            and self.move_type in ("out_invoice", "out_refund")
            and self.partner_id
            and self.state != "cancel"
            and self.invoice_line_ids.filtered(lambda x: not x.display_type)
        ):
            return xml_format
        else:
            return False
