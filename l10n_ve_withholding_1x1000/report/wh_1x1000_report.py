#~ # -*- coding: utf-8 -*-
from openerp.report import report_sxw
import time
from datetime import datetime, timedelta
import datetime as dt


class wh_1x1000_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        
        super(wh_src_report, self).__init__(cr, uid, name, context)
        self.localcontext.update(
        {
            'get_empresa':self.get_empresa,
           
                    })
        self.context= context
        

    def get_empresa(self, partner_id):
        """ Get information company
        """
        partner_id = isinstance(partner_id, (int,long)) and [partner_id] or partner_id
        rp_obj = self.pool.get('res.partner')
        row = rp_obj.browse(self.cr, self.uid, partner_id[0])
        row = rp_obj._find_accounting_partner(row)
        return {
            'street':row.street,
            'phone':row.phone,
            'fax':row.fax,
            'email':row.email,
            'city':row.city,
            'name':row.name,
            'country':row.country_id.name,
            } 

report_sxw.report_sxw('report.wh.1x1000.report',
                    'account.wh.1x1000',
                     parser= wh_1x1000_report,
                    #~ header= 'internal',
                    rml= 'l10n_ve_withholding_1x1000/report/wh_1x1000_report.rml'
                    )
