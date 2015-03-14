# -*- encoding: utf-8 -*-

import time
from openerp.report import report_sxw


class fb_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_lines': self._get_lines,
        })

    def _get_lines(self, fiscal_book):
        """
        Dummy method thath will return list of book lines to be print in the
        report.
        @return list of browseables
        """
        # my_fb.fbl_ids
        print ' --- estuve aqui'
        return True

report_sxw.report_sxw(
    'report.report_fiscal_book_purchas',
    'res.partner',
    'addons/loc_ve/report/fiscal_book_purchase_report.rml',
    parser=fb_parser,
    header=False)

report_sxw.report_sxw(
    'report.report_fiscal_book_sale',
    'res.partner',
    'addons/loc_ve/report/fiscal_book_sale_report.rml',
    parser=fb_parser,
    header=False)
