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
        group_max = self.get_group_size(fb_brw)
        if len(fb_brw.fbl_ids) <= group_max:
            lines = [line.read([])[0] for line in fb_brw.fbl_ids]
            lines = self.get_unidecode_lines(lines)
            # self._print_book([], lines, [])
            return [{'init': [], 'lines': lines, 'partial_total': []}]

        res = []

        line_groups = self.get_line_groups(fb_brw, group_max)
        last_page = len(line_groups)
        for page, subgroup in enumerate(line_groups, 1):
            cr.execute('SAVEPOINT report_original_fb_' + str(page))
            lines = self.get_unidecode_lines(subgroup)
            inv_ids = [line.get('invoice_id')[0]
                       for line in subgroup if line.get('invoice_id')]
            self.context.update(
                call_from_report=1, report_group_inv_ids=inv_ids)
            fb_obj.update_book(cr, uid, [fb_brw.id], context=self.context)
            fb_brw.refresh()

            begin_line = self.get_begin_line(res)
            partial_total = \
                page != last_page and self.get_partial_total(fb_brw) or []
            res.append({'init': begin_line,
                        'lines': lines,
                        'partial_total': partial_total})
            self._print_book(begin_line, lines, partial_total)
            cr.execute('ROLLBACK TO SAVEPOINT report_original_fb_' + str(page))
        return res

    def get_unidecode_lines(self, lines_dict):
        """
        @return unidecode lines from fiscal book.
        """
        for line in lines_dict:
            line['parnter_name'] = unicode(line['partner_name'])
        return lines_dict

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
                line_subset.extend(line.read([]))
                group_height += line_height
            else:
                # print ' --- group height', group_height
                res.append(line_subset)
                line_subset = line.read([])
                group_height = line_height
        res.append(line_subset)
        return res

    def _print_book(self, begin_line, lines, partial_total):
        self._print_book_lines(begin_line, 'init')
        self._print_book_lines(lines, 'lines')
        self._print_book_lines(partial_total, 'partial')

    def _print_book_lines(self, lines, title):
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

        print title, '\n',
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

    def get_partial_total(self, fb_brw):
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
            group = 35
        else:
            group = 48
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
                if len(unicode(getattr(line, field))) <= max_width:
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
