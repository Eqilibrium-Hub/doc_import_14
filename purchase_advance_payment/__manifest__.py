# -*- coding: utf-8 -*-
{
    'name': "Purchase Advance Payment",
    'author':
        'ENZAPPS',
    'summary': """
This module is for Creating Advance Payment For Purchase.
""",

    'description': """
This module is for Creating Advance Payment For Purchase against the Vendors.
    """,
    'website': "",
    'category': 'base',
    'version': '14.0',
    'depends': ['base', 'account', 'product', 'purchase',],
    "images": ['static/description/icon.png'],
    'data': [
        'views/advance_payment.xml',
        'views/sale_order.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
