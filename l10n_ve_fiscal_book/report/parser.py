# -*- encoding: utf-8 -*-
from openerp.report import report_sxw
import time

class Dict2Obj:
    def __init__(self, entries):
        self.__dict__.update(entries)

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
        group = self.get_group_size()
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
            fb_report = self.dict2obj(fb_dict)
            res += [fb_report]
            cr.execute('ROLLBACK TO SAVEPOINT report_original_fb_' + str(page))
        return res

    def get_group_size(self):
        """
        @return the number of lines per page in the report.
        """
        group = 19
        return group

    def dict2obj(self, data):
        """
        convert a dictionary to an object. Check for the openerp items in the
        dictionary and convert them to be redeable.
            - if is a o2m field a read will return a tuple (id, value). So we
              will take the second element of the tuple the value.
        @return a python obj
        """
        for (key, value) in data.iteritems():
            if (isinstance(value, (list)) and value
                    and isinstance(value[0], (dict))):
                data[key] = [self.dict2obj(val) for val in value]
            if isinstance(value, (dict)):
                data[key] = self.dict2obj(value)
            if isinstance(value, (tuple)):
                data[key] = value[1]
        return Dict2Obj(data)

    def get_book_lines(self, fb_brw):
        """
        Extract lines data from the fiven fiscal book
        @param fb_brw: fiscal book browseable.
        @return list of dictionaries. every dictionary represent a book line.
        """
        cr, uid = self.cr, self.uid
        fbl_obj = self.pool.get('fiscal.book.line')
        line_ids = [line.id for line in fb_brw.fbl_ids]
        lines = fbl_obj.read(cr, uid, line_ids, [])
        res = [line for line in lines]
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
