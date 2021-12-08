# -*- coding: utf-8 -*-
{
    'name': "Arabic Numbers",
    'author':
        'Enzapps',
    'summary': """
    This is a module is for changing field value to arabic
""",

    'description': """
        This is a module is for changing field value to arabic
    """,
    'website': "www.enzapps.com",
    'category': 'base',
    'version': '14.0',
    'depends': ['base','contacts','sale','sale_management','sale_stock','stock','product','account'],
    "images": ['static/description/icon.png'],
    'data': [
        'views/account_invoice.xml',
        'views/sale_order.xml',
],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
