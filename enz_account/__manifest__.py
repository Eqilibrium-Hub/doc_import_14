# -*- coding: utf-8 -*-
{
    'name': 'Accounts',
    'version': '14.0.1.0.1',
    'summary': 'Accounts',
    'description': 'Accounts',
    'live_test_url': 'e',
    'category': '',
    'author': 'Vignesh',
    'maintainer': 'Enzapps',
    'company': 'Enzapps',
    'website': 'https://www.enzapps.com',
    'depends': [
        'base', 'sale_management', 'contacts', 'account', 'purchase', 'stock', 'hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'views/accounting.xml',
        'views/journal_report.xml',
        'views/tax.xml',
        'views/statement.xml',
        'views/opening_balance.xml',
        'data/seq.xml',
        'reports/reports.xml',
        'reports/estimate_report.xml',

        # 'views/contacts.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
