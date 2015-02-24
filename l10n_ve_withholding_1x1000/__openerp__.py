#!/usr/bin/python
# -*- encoding: utf-8 -*-

{
    "name" : "Retencion 1 x 1000",
    "version" : "0.2",
    "author" : "Thinkasoft",
    "category" : "Generic Modules",
    "website": "http://www.thinkasoft.com/",
    "description": '''Retencion de impuesto 1 x 1000 segun legislacion venezolana''',
    "depends" : [
                "base",
                "account",
                "l10n_ve_withholding",
                ],
    "init_xml" : [],
    "demo_xml" : [
        'demo/demo_journals.xml',
        'demo/demo_accounts.xml',
        'demo/demo_company.xml',
    ], 
    "test": [
        'test/aws_customer.yml',
        'test/aws_supplier.yml',
    ],
    "update_xml" : [
        'security/wh_1x1000_security.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_retention_view.xml',
        'view/wh_1x1000_view.xml',
        'view/account_invoice_view.xml',
        'view/company_view.xml',
        'view/partner_view.xml',
        'workflow/l10n_ve_wh_1x1000_wf.xml',
        'report/wh_1x1000_report.xml',
        
    ],
    "active": False,
    "installable": True,
}
