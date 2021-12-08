# -*- coding: utf-8 -*-
{
    'name': "Help Desk Support",
    'author':
        'ENZAPPS',
    'summary': """
This module is for Help Desk Support.
""",

    'description': """
        This module is for Help desk Support.
    """,
    'website': "",
    'category': 'base',
    'version': '12.0',
    'depends': ['base', 'mail', 'portal'],
    "images": ['static/description/icon.png'],
    'data': [
        'security/help_desk_security.xml',
        'security/ir.model.access.csv',
        'reports/ticket_report_view.xml',
        'reports/ticket_report.xml',
        # 'reports/pda_report_view.xml',
        # 'reports/pda_report.xml',
        # 'data/pda_email_template.xml',
        # 'data/pre_arrival_email_template.xml',
        'data/sequences.xml',
        'data/ticket_template.xml',
        'data/test_email_template.xml',
        'views/helpdesk_ticket.xml',
        'views/ticket_support.xml',
        'views/assign_work.xml',
        # 'views/port_reg.xml',
        # 'views/res_partner_inherit.xml',
        # 'views/pda_form.xml',
        # 'views/inherited_menus.xml',
        # 'views/health_agency.xml',
        # 'views/pre_arrival.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
