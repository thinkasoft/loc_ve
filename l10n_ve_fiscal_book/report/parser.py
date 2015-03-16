# -*- encoding: utf-8 -*-
from openerp.report import report_sxw
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
        group = self.get_group_size()
        if len(fb_brw.fbl_ids) <= group:
            return [fb_brw]

        cr, uid = self.cr, self.uid
        fbl_obj = self.pool.get('fiscal.book.line')
        res = []
        all_line_brws = fb_brw.fbl_ids

        # Divide fiscal book lines is groups.
        line_groups = []
        while all_line_brws:
            line_subset = all_line_brws[:group]
            line_groups.append(line_subset)
            all_line_brws = all_line_brws[group:]
        last_page = len(line_groups)
        for page, subgroup in enumerate(line_groups, 1):
            line_ids = [line.id for line in subgroup]
            lines = fbl_obj.read(cr, uid, line_ids, [])
            begin_line = self.get_begin_line(res)
            partial_total = \
                page != last_page and self.get_partial_total(lines) or []
            res.append({'init': begin_line,
                        'lines': lines,
                        'partial_total': partial_total})
        return res

    def get_begin_line(self, res):
        """
        @return list of dictionary.
        """
        if not res:
            return []
        line = res[-1].get('partial_total')
        line[0].update(partner_name='VIENEN')
        return line

    def get_total_columns(self):
        """
        @return the fields that are print the total column of the report.
        """
        columns = [
            'total_with_iva', 'vat_sdcf', 'vat_exempt', 'vat_general_base',
            'vat_general_tax', 'vat_reduced_base', 'vat_reduced_tax',
            'vat_additional_base', 'vat_additional_tax', 'vat_sdcf',
            'vat_exempt', 'vat_general_base', 'vat_general_tax',
            'get_wh_debit_credit', 'wh_rate', 'get_wh_vat',
        ]
        return columns

    def get_partial_total(self, lines):
        """
        @param list of dictionaries
        """
        total_columns = self.get_total_columns()
        line = {}.fromkeys(total_columns, 0.0)
        line.update(partner_name='VAN')
        for ldata in lines:
            for field in total_columns:
                try:
                    line[field] += ldata[field]
                except:
                    import pdb
                    pdb.set_trace()
        return [line]

    def get_group_size(self):
        """
        @return the number of lines per page in the report.
        """
        group = 19
        return group



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
