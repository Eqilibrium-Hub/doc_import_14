# -*- coding: utf-8 -*-
{
    'name': "Galvanization Invoice Report",
    'author':
        'ENZAPPS',
    'summary': """
This module is for printing Invoice Format For Galvanization.
""",

    'description': """
        This module is for printing E-Invoice Format.
    """,
    'website': "www.enzapps.com",
    'category': 'base',
    'version': '14.0',
    # 'depends':['base','account','sale','sale_management','uom_unece','base_unece','account_tax_unece','base_vat_sanitized','onchange_helper','base_iban','base_bank_from_iban','base_business_document_import','account_invoice_import','base_ubl_payment','account_payment_partner','account_invoice_import_ubl','account_invoice_ubl','enz_system_config','ubl_mail','arabic_numbers','arabic_strings',],
    'depends':['base','account','sale','sale_management','uom_unece','base_unece','account_tax_unece','base_vat_sanitized','onchange_helper','base_iban','base_bank_from_iban','base_business_document_import','account_invoice_import','base_ubl_payment','account_payment_partner','account_invoice_import_ubl','account_invoice_ubl'],
    "images": [],
    'data': [
            # 'views/inherit_account_move.xml'
            'views/account_move.xml',
            'reports/report.xml',
            'reports/report_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
