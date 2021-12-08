# -*- coding: utf-8 -*-
{
    'name': "UBL PDF Mail",
    'author':
        'ENZAPPS',
    'summary': """
This module is for Sending UBL And PDF Format to Admin mail.
""",

    'description': """
This module is for Sending UBL And PDF Format to Admin mail.
    """,
    'website': "",
    'category': 'base',
    'version': '14.0',
    'depends': ['base', 'account', 'stock','mail'],
    "images": ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/admin_mail.xml',
        'views/account_move.xml',
        'views/einvoice_admin.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
