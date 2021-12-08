{
    "name": "AGC",
    "summary": "This Module is For AGC",
    "version": "14.0.1.3.5",
    "author": "Enzapps",
    "category": "base",
    "images": ["images/galvanisation.jpg"],
    "support": "info@enzapps.com",
    "website": "https://www.enzapps.com/",
    "depends": ['base', 'account','contacts', 'stock', 'product','sale', 'sale_management', 'purchase'],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/sequences.xml",
        "views/delivery.xml",
        "views/configuration.xml",
        "views/account_move.xml",
        "reports/report.xml",
        "reports/report_view.xml",

             ],
    "installable": True,
    "application":True,
}
