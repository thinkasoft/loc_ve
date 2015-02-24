#!/usr/bin/python
# -*- encoding: utf-8 -*-
{
    "name": "Retencion 1x1000 para la ley de Timbre Fiscal de Venezuela",
    "version": "0.1",
    "author": "Thinkasoft",
    "website": "http://thinkasoft.com",
    "category": 'Generic Modules/Accounting',
    "description": """Modulo para el manejo de retencion 1x1000 exigido por la leyes de venezuela
    """,
    'init_xml': [],
    "depends": ["l10n_ve_withholding"],
    'update_xml': [
        'security/wh_timbre_security.xml',
        'security/ir.model.access.csv',
        'view/account_invoice_view.xml',
        'view/partner_view.xml',
        'view/wh_timbre_view.xml',
        'data/wh_timbre_sequence.xml',
        'report/wh_timbre_report.xml',
        'workflow/l10n_ve_wh_timbre_wf.xml',
    ],
    'data': [
        'data/wh_timbre_sequence.xml',
    ],
    'demo_xml': [
        'demo/demo_accounts.xml',
        'demo/demo_partners.xml',
        'demo/demo_journal.xml',
    ],
    'test': [
        'test/awm_supplier.yml',
        'test/awm_customer.yml'
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
