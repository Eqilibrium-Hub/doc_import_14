# -*- coding: utf-8 -*-
{
    'name': "Inventory Sale Purchase",
    'author':
        'YARMIZ',
    'summary': """
This module will help to Show the Complete Sale And Purchase Current stock information.
""",

    'description': """
        Long description of module's purpose
    """,
    'website': "",
    'category': 'base',
    'version': '12.0',
    'depends': ['base','account',"stock","sale","purchase"],
    "images": ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_purchase.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
