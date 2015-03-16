# -*- encoding: utf-8 -*-
from openerp.report import report_sxw
import time
import pdb


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
        fbl_obj = self.pool.get('fiscal.book.line')
        group = self.get_group_size()
        if len(fb_brw.fbl_ids) <= group:
            line_ids = [line.id for line in fb_brw.fbl_ids]
            lines = fbl_obj.read(cr, uid, line_ids, [])
            self._print_book([], lines, [])
            return [{'init': [], 'lines': lines, 'partial_total': []}]

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
            begin_line =  self.get_begin_line(res)
            partial_total = \
                page != last_page and self.get_partial_total(lines) or []
            res.append({'init': begin_line,
                        'lines': lines,
                        'partial_total': partial_total})
            self._print_book(begin_line, lines, partial_total)

        return res

    def _print_book(self, begin_line, lines, partial_total):
        print '\ninit'
        self._print_book_lines(begin_line)
        print 'lines\n',
        for item in lines:
            self._print_book_lines([item])
        print 'partial'
        self._print_book_lines(partial_total)

    def _print_book_lines(self, line):
        if not line:
            print False
            return False
        line = line[0]
        print (
            line.get('rank'), line.get('partner_name'),
            line.get('total_with_iva'), line.get('vat_sdcf'),
            line.get('vat_exempt'), line.get('vat_general_base'),
            line.get('vat_general_tax'), line.get('vat_reduced_base'),
            line.get('vat_reduced_tax'), line.get('vat_additional_base'),
            line.get('vat_additional_tax'), line.get('vat_sdcf'),
            line.get('vat_exempt'), line.get('vat_general_base'),
            line.get('vat_general_tax'), line.get('get_wh_debit_credit'),
            line.get('wh_rate'), line.get('get_wh_vat')
        )
        return True

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
                line[field] += ldata[field]
        return [line]

    def get_group_size(self):
        """
        @return the number of lines per page in the report.
        """
        group = 17
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
