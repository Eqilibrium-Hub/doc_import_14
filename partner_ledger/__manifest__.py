# -*- coding: utf-8 -*-
{
    'name': "ENZ Accounting",
    'author':
        'Enzapps',
    'summary': """
This module will help to View the All Accounting Reports with Complete information.
""",

    'description': """
        Long description of module's purpose
    """,
    'website': "",
    'category': 'base',
    'version': '12.0',
    'depends': ['base', 'account', 'sale', 'purchase', 'grouped_product', 'inventory_sale_purchase', 'grouped_products_custom', 'opening_balance_customers_saudhi', 'advanced_common_day_book', 'enz_account'],
    "images": ['static/description/icon.png'],
    'data': [
        'security/ir.model.access.csv',
        # 'security/ledger_group.xml',
        'views/assets.xml',
        'views/partner_ledger.xml',
        'views/supplier_ledger.xml',
        'views/cash_book.xml',
        'views/sales_report.xml',
        'views/purchase_report.xml',
        'views/customer_aged_repo.xml',
        'views/menu.xml',
        'report/collection.xml',
        'report/ledger.xml',

    ],
    'demo': [
    ],
    "qweb": ["static/src/xml/building_room_summary.xml"],
    'installable': True,
    'application': True,
}
