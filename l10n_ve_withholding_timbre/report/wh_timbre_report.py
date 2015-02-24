#!/usr/bin/python
# -*- encoding: utf-8 -*-

import time
from openerp.report import report_sxw
from openerp.osv import osv
import openerp.pooler
from openerp.tools.translate import _ 

class wh_timbre_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(wh_timbre_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_partner_addr': self._get_partner_addr,
            'get_rif': self._get_rif
        })

    def _get_partner_addr(self, idp=False):
        """ Return partner address
        """
        if not idp:
            return []

        addr_obj = self.pool.get('res.partner')
        addr_inv = _('NO INVOICE ADDRESS DEFINED')
        if idp:                
            addr = addr_obj.browse(self.cr,self.uid, idp)
            addr_inv =addr.type == 'invoice' and  (addr.street or '')+' '+(addr.street2 or '')+' '+(addr.zip or '')+ ' '+(addr.city or '')+ ' '+ (addr.country_id and addr.country_id.name or '')+ ', TELF.:'+(addr.phone or '') or _('NO INVOICE ADDRESS DEFINED')
        return addr_inv 


    def _get_rif(self, vat=''):
        """ Return partner rif
        """
        if not vat:
            return []
        return vat[2:].replace(' ', '')

    
      
report_sxw.report_sxw(
    'report.wh.timbre.report',
    'account.wh.timbreci',
    rml='l10n_ve_withholding_timbre/report/wh_timbre_report.rml',
    parser=wh_timbre_report,
    header=False
)      
