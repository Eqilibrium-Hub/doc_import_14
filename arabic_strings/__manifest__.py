# -*- coding: utf-8 -*-
{
    'name': "Arabic Strings",
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
        'views/contacts.xml',
        'views/product.xml',
        'views/res_company.xml',
        # 'views/account_move.xml',
],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
