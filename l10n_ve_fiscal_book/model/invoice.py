#!/usr/bin/python
# -*- encoding: utf-8 -*-
###############################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved
################ Credits ######################################################
#    Coded by:       Luis Escobar <luis@vauxoo.com>
#                    Tulio Ruiz <tulio@vauxoo.com>
#                    Katherine Zsoral <katherine.zaoral@vauxoo.com>
#    Planified by: Nhomar Hernandez
###############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from openerp.osv import osv, fields
from openerp.tools.translate import _


class account_invoice(osv.osv):
    _inherit = "account.invoice"

    _columns = {
        'fb_id': fields.many2one('fiscal.book', 'Fiscal Book',
                                 help='Fiscal Book where this line is ' \
                                 'related to'),
        'issue_fb_id': fields.many2one('fiscal.book', 'Fiscal Book',
                                       help='Fiscal Book where this invoice ' \
                                       'needs to be add'),
    }

    def action_cancel(self, cr, uid, ids, context=None):
        """ Verify first in the invoice have a fiscal book associated and if
        the state of the book is in cancel. """
        context = context or {}
        for inv_brw in self.browse(cr, uid, ids, context=context):
            if not inv_brw.fb_id or (inv_brw.fb_id and inv_brw.fb_id.state == 'cancel'):
                super(account_invoice, self).action_cancel(cr, uid, ids,
                                                           context=context)
            else:
                raise osv.except_osv(_("Error!"),
                _("You can't cancel an invoice that is loaded in a processed "
                  "Fiscal Book (%s). You need to go to Fiscal Book and set "
                  "the book to Cancel. Then you could be able to cancel the "
                  "invoice." % (inv_brw.fb_id.state,)))
        return True

    def copy(self, cur, uid, id, default=None, context=None):
        """
        Overwrite the copy orm method to blank the fiscal book field when
        a invoice is copy. Also if a invoice have benn remove from a fiscal
        book the issue_fb_id is add, if a duplicate this invoice that info os
        issue will be garbage so I clean it too.
        """
        context = context or {}
        default = default or {}
        default.update(fb_id=False)
        if default.get('issue_fb_id', False):
            default.update(issue_fb_id=False)
        res = super(account_invoice, self).copy(
            cur, uid, id, default=default, context=context)
        return res

    def search(self, cr, user, args, offset=0, limit=None, order=None,
               context=None, count=False):
        """
        Overwrite this search method to only retrive only a subset of invoices.
        @return list of ids
        """
        context = context or {}
        if context.get('call_from_report', False):
            report_inv_ids = context.get('report_group_inv_ids', False)
            if report_inv_ids:
                args += [('id', 'in', report_inv_ids)]
        res = super(account_invoice, self).search(
            cr, user, args, offset=offset, limit=limit, order=order,
            context=context, count=count)
        return res
