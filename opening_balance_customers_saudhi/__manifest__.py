# -*- coding: utf-8 -*-
{
    'name': "Opening Balance For Customers(Saudhi)",
    'author':
        'YARMIZ',
    'summary': """
This module will help to assign the targets to sales persons
""",

    'description': """
        Long description of module's purpose
    """,
    'website': "",
    'category': 'base',
    'version': '12.0',
    'depends': ['base','account',"stock","contacts"],
    "images": ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        'data/seq.xml',
        'views/opening_bal.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
