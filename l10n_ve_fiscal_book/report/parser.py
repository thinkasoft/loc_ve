# -*- encoding: utf-8 -*-
from openerp.report import report_sxw
from openerp.osv import osv
import time


class fb_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        context = context or {}
        super(fb_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_partial_books': self.get_partial_books,
            'context': context,
        })
        self.context = context

    def get_partial_books(self, fb_brw):
        """
        This method divide a fiscal book in groups of lines.
        @return list of dictionaries
        """
        cr, uid = self.cr, self.uid
        fb_obj = self.pool.get('fiscal.book')
        group = 19
        res = []
        all_line_brws = fb_brw.fbl_ids

        if len(all_line_brws) <= 19:
            return [fb_brw]

        # Divide fiscal book lines is groups.
        line_groups = []
        while all_line_brws:
            line_subset = all_line_brws[:group]
            line_groups.append(line_subset)
            all_line_brws = all_line_brws[group:]
        for page, subgroup in enumerate(line_groups):
            cr.execute('SAVEPOINT report_original_fb_' + str(page))
            inv_ids = [line.invoice_id.id for line in subgroup]
            self.context.update(
                call_from_report=1, report_group_inv_ids=inv_ids)
            fb_obj.update_book(cr, uid, [fb_brw.id], context=self.context)
            fb_brw.refresh()
            fb_dict = fb_obj.read(cr, uid, fb_brw.id, [])
            fb_dict.update({'fbl_ids': self.get_book_lines(fb_brw)})
            res += [fb_dict]
            cr.execute('ROLLBACK TO SAVEPOINT report_original_fb_' + str(page))

        import pdb
        pdb.set_trace()
        # return res
        raise osv.except_osv('WIP', 'Functionality Still in Development')

    def get_book_lines(self, fb_brw):
        """
        Extract lines data from the fiven fiscal book
        @param fb_brw: fiscal book browseable.
        @return list of dictionaries. every dictionary represent a book line.
        """
        cr, uid = self.cr, self.uid
        fbl_obj = self.pool.get('fiscal.book.line')
        line_ids = [line.id for line in fb_brw.fbl_ids]
        return fbl_obj.read(cr, uid, line_ids, [])

report_sxw.report_sxw(
    'report.fiscal.book.purchase',
    'fiscal.book',
    'addons/loc_ve/report/fiscal_book_purchase_report.rml',
    parser=fb_parser,
    header=False)

report_sxw.report_sxw(
    'report.fiscal.book.sale',
    'fiscal.book',
    'addons/loc_ve/report/fiscal_book_sale_report.rml',
    parser=fb_parser,
    header=False)
