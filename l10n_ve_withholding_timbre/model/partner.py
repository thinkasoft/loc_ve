#!/usr/bin/python
# -*- encoding: utf-8 -*-

from openerp.osv import fields, osv

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'property_wh_timbreci_payable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Purchase local withholding account",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="This account will be used debit local withholding amount"),
        'property_wh_timbreci_receivable': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Sale local withholding account",
            method=True,
            view_load=True,
            domain="[('type', '=', 'other')]",
            help="This account will be used credit local withholding amount"),

    }
