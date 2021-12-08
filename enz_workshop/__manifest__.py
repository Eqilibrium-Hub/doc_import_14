# -*- coding: utf-8 -*-
{
    'name': "Enz Workshop",
    'author':
        'Enzapps',
    'summary': """
    This is a module is for Work shop managment.
""",

    'description': """
        This is a module is for supporting Work shop managment.
    """,
    'website': "www.enzapps.com",
    'category': 'base',
    'version': '12.0',
    'depends': ['base','account', 'stock', 'product','sale', 'sale_management', 'purchase', 'contacts', 'hr', 'hr_expense','fleet'],
    "images": [],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/configuration.xml',
        'views/job_order.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
