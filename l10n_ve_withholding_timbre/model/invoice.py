#!/usr/bin/python
# -*- encoding: utf-8 -*-

import time
from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def _get_move_lines(self, cr, uid, ids, to_wh, period_id,
                            pay_journal_id, writeoff_acc_id,
                            writeoff_period_id, writeoff_journal_id, date,
                            name, context=None):
        """ Generate move lines in corresponding account                            
        @param to_wh: whether or not withheld                                   
        @param period_id: Period                                                
        @param pay_journal_id: pay journal of the invoice                       
        @param writeoff_acc_id: account where canceled                          
        @param writeoff_period_id: period where canceled                        
        @param writeoff_journal_id: journal where canceled                      
        @param date: current date                                               
        @param name: description                                                
        """

        context = context or {}
        res = super(account_invoice, self)._get_move_lines(cr, uid, ids, to_wh,
                            period_id, pay_journal_id, writeoff_acc_id,
                            writeoff_period_id, writeoff_journal_id, date,
                            name, context=context)
        if context.get('timbre_wh', False):
            rp_obj = self.pool.get('res.partner')
            acc_part_brw = rp_obj._find_accounting_partner(to_wh.invoice_id.partner_id)
            invoice = self.browse(cr, uid, ids[0])
            types = {
              'out_invoice': -1,
              'in_invoice': 1,
              'out_refund': 1,
              'in_refund': -1
            }
            direction = types[invoice.type]
            if to_wh.retention_id.type == 'in_invoice':
                acc = acc_part_brw.property_wh_timbreci_payable and acc_part_brw.property_wh_timbreci_payable.id or False
            else:
                acc = acc_part_brw.property_wh_timbreci_receivable and acc_part_brw.property_wh_timbreci_receivable.id or False
            if not acc:
                raise osv.except_osv(_('Missing Local Account in Partner!'),_("Partner [%s] has missing Local account. Please, fill the missing field") % (acc_part_brw.name,))
            res.append((0, 0, {
                'debit': direction * to_wh.amount < 0 and
                         - direction * to_wh.amount,
                'credit': direction * to_wh.amount > 0 and
                          direction * to_wh.amount,
                'partner_id': acc_part_brw.id,
                'ref': invoice.number,
                'date': date,
                'currency_id': False,
                'name': name,
                'account_id': acc,
            }))
        return res

    def _retenida_timbreci(self, cr, uid, ids, name, args, context=None):
        """ Check that all is well in the log lines
        """
        context = context or {}
        res = {}
        for id in ids:
            res[id] = self.test_retenida_timbre(cr, uid, [id], 'rettimb')
        return res

    def test_retenida_timbre(self, cr, uid, ids, *args):
        """ Check that all lines having their share account
        """
        type2journal = {'out_invoice': 'timb_sale',
                        'out_refund': 'timb_sale',
                        'in_invoice': 'timb_purchase',
                        'in_refund': 'timb_purchase'}
        type_inv = self.browse(cr, uid, ids[0]).type
        type_journal = type2journal.get(type_inv, 'timb_purchase')
        res = self.ret_payment_get(cr, uid, ids)
        if not res:
            return False
        ok = True

        cr.execute('select \
                l.id \
            from account_move_line l \
                inner join account_journal j on (j.id=l.journal_id) \
            where l.id in (' + ','.join(map(str, res)) + ') and j.type=' +
            '\'' + type_journal + '\'')
        ok = ok and  bool(cr.fetchone())
        return ok

    def _get_inv_timbreci_from_line(self, cr, uid, ids, context=None):
        """ Return invoice from journal items
        """
        context = context or {}
        move = {}
        aml_brw = self.pool.get('account.move.line').browse(cr, uid, ids)
        for line in aml_brw:
            if line.reconcile_partial_id:
                for line2 in line.reconcile_partial_id.line_partial_ids:
                    move[line2.move_id.id] = True
            if line.reconcile_id:
                for line2 in line.reconcile_id.line_id:
                    move[line2.move_id.id] = True
        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid,
                         [('move_id', 'in', move.keys())], context=context)
        return invoice_ids

    def _get_inv_timbreci_from_reconcile(self, cr, uid, ids, context=None):
        """ Return invoice from reconciled lines
        """
        context = context or {}
        move = {}
        amr_brw = self.pool.get('account.move.reconcile').browse(cr, uid, ids)
        for r in amr_brw:
            for line in r.line_partial_ids:
                move[line.move_id.id] = True
            for line in r.line_id:
                move[line.move_id.id] = True

        invoice_ids = []
        if move:
            invoice_ids = self.pool.get('account.invoice').search(cr, uid,
                          [('move_id', 'in', move.keys())], context=context)
        return invoice_ids

    def action_cancel(self, cr, uid, ids, context=None):
        """ Verify first if the invoice have a non cancel local withholding doc.
        If it has then raise a error message. """
        context = context or {}
        for inv_brw in self.browse(cr, uid, ids, context=context):
            if not inv_brw.wh_timbre_id:
                super(account_invoice, self).action_cancel(cr, uid, ids,
                                                           context=context)
            else:
                raise osv.except_osv(_("Error!"),
                _("You can't cancel an invoice that have non cancel"
                  " Local Withholding Document. Needs first cancel the invoice"
                  " Local Withholding Document and then you can cancel this"
                  " invoice."))
        return True

    _columns = {
        'wh_local': fields.function(_retenida_timbreci, method=True,
            string='Local Withholding', type='boolean',
            store={
              'account.invoice':
                (lambda self, cr, uid, ids, c={}: ids, None, 50),
              'account.move.line': (_get_inv_timbreci_from_line, None, 50),
              'account.move.reconcile':
                (_get_inv_timbreci_from_reconcile, None, 50),
            },
            help="The account moves of the invoice have been withheld with \
            account moves of the payment(s)."),
        'wh_timbre_id': fields.many2one('account.wh.timbreci', 'Wh. Municipality',
            readonly=True, help="Withholding timbre."),

    }
