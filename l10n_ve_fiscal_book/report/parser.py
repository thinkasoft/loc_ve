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
        fbl_obj = self.pool.get('fiscal.book.line')
        group_max = self.get_group_size(fb_brw)
        if len(fb_brw.fbl_ids) <= group_max:
            line_ids = [line.id for line in fb_brw.fbl_ids]
            lines = fbl_obj.read(cr, uid, line_ids, [])
            # self._print_book([], lines, [])
            return [{'init': [], 'lines': lines, 'partial_total': []}]

        res = []
        line_groups = self.get_line_groups(fb_brw, group_max)

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
            self._print_book(begin_line, lines, partial_total)
        return res

    def get_line_groups(self, fb_brw, group_max):
        """
        Divide fiscal book lines in groups.
        @return list of lists.
        """
        height = self.get_lines_height(fb_brw)
        res = []
        line_subset = []
        group_height = 0
        for line in fb_brw.fbl_ids:
            line_height = height[line.id]
            if line_height + group_height <= group_max:
                line_subset.append(line)
                group_height += line_height
            else:
                # print ' --- group height', group_height
                res.append(line_subset)
                line_subset = [line]
                group_height = line_height
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

        total_columns = self.get_total_columns()
        line = {}.fromkeys(total_columns, 0.0)
        if res:
            line.update(res[-1].get('partial_total')[0])
        line.update(partner_name='VIENEN')
        return [line]

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

    def get_group_size(self, fb_brw):
        """
        @return the number of lines per page in the report.
        """
        if fb_brw.type == 'purchase':
            group = 35
        else:
            group = 47
        return group

    def get_column_width(self, fb_brw):
        """
        @return dictionray (columnd field, field value len).
        """
        if fb_brw.type == 'purchase':
            columns_width = dict(
                # rank=len('Linea'),
                # void_form=len('T. Doc.'),
                # emission_date=len('Fecha Doc.'),
                invoice_number=len('Numero de Documento'),
                nro_ctrl=len('Numero Control'),
                affected_invoice=len('Afectada'),
                partner_name=26,
                partner_vat=10,
                # total_with_iva=len('Documento'),
                # vat_sdcf=len('SDCF'),
                # vat_exempt=len('Exento'),
                # vat_general_base=len('imponible'),
                # vat_general_tax=len('debito'),
                # vat_reduced_base=len('imponible'),
                # vat_reduced_tax=len('debito'),
                # vat_additional_base=len('imponible'),
                # vat_additional_tax=len('debito'),
            )
        elif fb_brw.type == 'sale':
            columns_width = dict(
                # rank=len('Linea'),
                # void_form=len('T. Doc.'),
                # emission_date=len('Fecha Doc.'),
                # invoice_number=len('Numero de Documento'),
                # nro_ctrl=len('Numero Control'),
                # affected_invoice=len('Afectada'),
                partner_name=43,
                partner_vat=10,
                # total_with_iva=len('Documento'),
                # vat_sdcf=len('SDCF'),
                # vat_exempt=len('Exento'),
                # vat_general_base=len('imponible'),
                # vat_general_tax=len('debito'),
                # vat_reduced_base=len('imponible'),
                # vat_reduced_tax=len('debito'),
                # vat_additional_base=len('imponible'),
                # vat_additional_tax=len('debito'),
            )
        return columns_width

    def get_lines_height(self, fb_brw):
        """
        @return groups
        """
        columns_width = self.get_column_width(fb_brw)
        res = dict()
        for line in fb_brw.fbl_ids:
            line_height = []
            for (field, max_width) in columns_width.iteritems():
                if len(str(getattr(line, field))) <= max_width:
                    line_height += [1]
                else:
                    line_height += [2]
            res[line.id] = max(line_height)
        return res

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
