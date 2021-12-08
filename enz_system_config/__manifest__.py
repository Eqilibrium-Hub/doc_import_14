# -*- coding: utf-8 -*-
{
    'name': "EnzSystem Configuration",
    'author':
        'ENZAPPS',
    'summary': """
This module is for Managing the Einvoicing Default Values.
""",

    'description': """
This module is for Managing the Einvoicing Default Values.
    """,
    'website': "",
    'category': 'base',
    'version': '14.0',
    'depends': ['base', 'account', 'stock', 'product', 'sale', 'sale_management', 'purchase', 'contacts','arabic_strings'],
    "images": ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/einvoice_config.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
