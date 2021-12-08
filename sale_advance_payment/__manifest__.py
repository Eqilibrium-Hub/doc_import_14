# -*- coding: utf-8 -*-
{
    'name': "Sale Advance Payment",
    'author':
        'ENZAPPS',
    'summary': """
This module is for Creating Advance Payment For Sales.
""",

    'description': """
This module is for Creating Advance Payment For Sales against the customer.
    """,
    'website': "",
    'category': 'base',
    'version': '14.0',
    'depends': ['base', 'account', 'product', 'sale', 'sale_management'],
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
