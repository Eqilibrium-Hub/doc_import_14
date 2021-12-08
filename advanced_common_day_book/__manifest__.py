# -*- coding: utf-8 -*-
{
    'name': "Advanced Common Day Book",
    'author':
        'Enzapps',
    'summary': """
    This is a module is for supporting Man Power Supply Companies
""",

    'description': """
        This is a module is for supporting Man Power Supply Companies
    """,
    'website': "www.enzapps.com",
    'category': 'base',
    'version': '12.0',
    'depends': ['base','sale_management','purchase','hr_expense'],
    "images": [],
    'data': [
        'security/ir.model.access.csv',
        'views/common_day_book.xml',
        'views/sales_report.xml',
        'views/purchases_report.xml',
        'views/report_expense.xml',
        'views/purchase_inherit.xml',
        'reports/common_day_book.xml',
        'reports/common_day_book_view.xml',
        'reports/common_day_book_ar.xml',
        'reports/common_day_book_view_ar.xml',
        'reports/sales_report_en.xml',
        'reports/sales_report_en_view.xml',
        'reports/purchase_report.xml',
        'reports/purchase_report_view.xml',
        'reports/expense_report.xml',
        'reports/expense_report_view.xml',




    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
