# -*- encoding: utf-8 -*-
from openerp.report import report_sxw
from collections import OrderedDict
import time
import math


class fb_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        context = context or {}
        super(fb_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_partial_books': self.get_partial_books,
            'get_wh_debit_credit': self.get_wh_debit_credit,
            'get_wh_sum': self.get_wh_sum,
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
        if not fb_brw.fbl_ids:
            return [{'init': [], 'lines': [], 'partial_total': []}]

        line_groups = self.get_line_groups(fb_brw)
        last_page = len(line_groups)
        if last_page == 1:
            # self._print_book(
            #     [], line_groups[0].get('report_lines'), [], line_groups[0])
            return [{'init': [],
                     'lines': line_groups[0].get('report_lines'),
                     'partial_total': []}]
        res = []
        for subgroup in line_groups:
            cr.execute('SAVEPOINT report_original_fb_' + str(
                subgroup.get('page')))
            inv_ids = [line.get('invoice_id')[0]
                       for line in subgroup.get('report_lines')
                       if line.get('invoice_id')]
            self.context.update(
                call_from_report=1, report_group_inv_ids=inv_ids)
            fb_obj.update_book(cr, uid, [fb_brw.id], context=self.context)
            fb_brw.refresh()
            begin_line = self.get_begin_line(res)
            partial_total = (subgroup.get('page') != last_page and
                             self.get_partial_total(fb_brw, begin_line) or [])
            res.append({'init': begin_line,
                        'lines': subgroup.get('report_lines'),
                        'partial_total': partial_total})
            # self._print_book(
            #     begin_line, subgroup.get('report_lines'), partial_total,
            #     subgroup)
            cr.execute('ROLLBACK TO SAVEPOINT report_original_fb_' + str(
                subgroup.get('page')))
        return res

    def prepare_report_lines(self, lines_dict):
        cr, uid = self.cr, self.uid
        iwdl_obj = self.pool.get('account.wh.iva.line')
        lines_dict = self.get_unidecode_lines(lines_dict)

        for line in lines_dict:
            line['iwdl_id'] = line['iwdl_id'] and iwdl_obj.browse(
                cr, uid, line['iwdl_id'][0])
        return lines_dict

    def get_unidecode_lines(self, lines_dict):
        """
        @return unidecode lines from fiscal book.
        """
        for line in lines_dict:
            line['parnter_name'] = unicode(line['partner_name'])
        return lines_dict

    def get_line_groups(self, fb_brw):
        """
        Divide fiscal book lines in groups.
        @return list of lists.
        """
        group_max = self.get_group_size(fb_brw)
        lines_height = self.get_lines_height(fb_brw)
        res = []
        line_subset = OrderedDict()
        group_height = 0
        first_page = group_max - 1
        other_page = group_max - 2
        page = 1

        page_max = first_page
        for (line, line_height) in lines_height.iteritems():
            if line_height + group_height <= page_max:
                line_subset.update([(line, line_height)])
                group_height += line_height
            else:
                # save group
                res.append(self.get_group(line_subset, group_height,
                                          page, page_max))
                # init new group
                line_subset = OrderedDict([(line, line_height)])
                group_height = line_height
                page_max = other_page
                page += 1
        res.append(self.get_group(line_subset, group_height, page, page_max))
        return res

    def get_group(self, line_subset, group_height, page, page_max):
        cr, uid = self.cr, self.uid
        fbl_obj = self.pool.get('fiscal.book.line')
        return dict(
            ids=line_subset.keys(),
            report_lines=self.prepare_report_lines(
                fbl_obj.read(cr, uid, line_subset.keys())),
            fbl_lines=len(line_subset.keys()),
            real_lines=sum(line_subset.values()),
            group_height=group_height,
            page=page,
            page_max=page_max)

    def _print_book(self, begin_line, lines, partial_total, group_info):
        ginfo = ['page', 'page_max', 'group_height', 'fbl_lines', 'real_lines']
        for key in ginfo:
            print key, group_info.get(key)
        print '\n'
        self._print_book_lines(begin_line, 'init')
        self._print_book_lines(lines, 'lines')
        self._print_book_lines(partial_total, 'partial')

    def _print_book_lines(self, lines, title):
        print title
        if not lines:
            print False
            return False
        total_columns = self.get_total_columns()
        normal_columns = [
            'rank', 'partner_name', 'total_with_iva', 'vat_sdcf',
            'vat_exempt', 'vat_general_base', 'vat_general_tax',
            'vat_reduced_base', 'vat_reduced_tax', 'vat_additional_base',
            'vat_additional_tax', 'vat_sdcf', 'vat_exempt', 'vat_general_base',
            'vat_general_tax', 'get_wh_debit_credit', 'wh_rate', 'get_wh_vat',
            'get_total_with_iva_sum', 'tp_sdcf_vat_sum', 'tp_exempt_vat_sum',
            'do_general_vat_base_sum', 'do_general_vat_tax_sum',
        ]
        columns = title == 'lines' and normal_columns or total_columns
        for line in lines:
            to_print = []
            for col in columns:
                to_print.append(line.get(col))
            print to_print
        return True

    def get_begin_line(self, res):
        """
        @return list of dictionary.
        """
        if not res:
            return []
        total_columns = self.get_total_columns()
        line = {}.fromkeys(total_columns, 0.0)
        line.update(res[-1].get('partial_total')[0])

        line.update(partner_name='VIENEN')
        return [line]

    def get_total_columns(self):
        """
        @return the fields that are print the total column of the report.
        """
        columns = [
            'get_total_with_iva_sum', 'imex_sdcf_vat_sum',
            'imex_exempt_vat_sum', 'imex_general_vat_base_sum',
            'imex_general_vat_tax_sum', 'imex_reduced_vat_base_sum',
            'imex_reduced_vat_tax_sum', 'imex_additional_vat_base_sum',
            'do_additional_vat_tax_sum',
            'imex_additional_vat_tax_sum',
            'ntp_additional_vat_tax_sum',
            'tp_additional_vat_tax_sum',
            'do_sdcf_vat_sum', 'do_exempt_vat_sum',
            'do_general_vat_base_sum', 'do_general_vat_tax_sum',
            'get_wh_debit_credit_sum', 'get_wh_sum'
        ]
        return columns

    def get_partial_total(self, fb_brw, begin_line):
        """
        @param list of dictionaries
        """
        total_columns = self.get_total_columns()
        line = {}.fromkeys(total_columns, 0.0)
        line.update(partner_name='VAN')
        for field in total_columns:
            line[field] = getattr(fb_brw, field)
        line['get_wh_debit_credit_sum'] = self.get_wh_debit_credit(fb_brw)
        line['get_wh_sum'] = self.get_wh_sum(fb_brw)

        if begin_line:
            for field in total_columns:
                line[field] += begin_line[0].get(field)
        return [line]

    def get_wh_debit_credit(self, fb_brw):
        """
        The get_wh_debit_credit_sum and get_wh_sum do not have the previos
        month lines. so this sumatory need to be done manually.
        @return (get_wh_debit_credit_sum, get_wh_sum)
        """
        get_wh_debit_credit_sum = 0.0
        for line in fb_brw.fbl_ids:
            get_wh_debit_credit_sum += line['get_wh_debit_credit']
        return get_wh_debit_credit_sum

    def get_wh_sum(self, fb_brw):
        """
        The get_wh_debit_credit_sum and get_wh_sum do not have the previos
        month lines. so this sumatory need to be done manually.
        @return (get_wh_debit_credit_sum, get_wh_sum)
        """
        get_wh_sum = 0.0
        for line in fb_brw.fbl_ids:
            get_wh_sum += line['get_wh_vat']
        return get_wh_sum

    def get_group_size(self, fb_brw):
        """
        @return the number of lines per page in the report.
        """
        if fb_brw.type == 'purchase':
            group = 36
            # TOTAL 38, but need to add one more for the total column
        else:
            group = 46
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
                # partner_vat=10,
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
        res = OrderedDict()
        for line in fb_brw.fbl_ids:
            line_height = []
            for (field, max_width) in columns_width.iteritems():
                height = len(unicode(getattr(line, field)))
                if height <= float(max_width):
                    line_height += [1]
                else:
                    line_height += [math.ceil(height/float(max_width))]
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
