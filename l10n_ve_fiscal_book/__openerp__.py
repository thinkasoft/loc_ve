
{
    "name" : "Fiscal Report For Venezuela",
    "version" : "0.5",
    "depends" : ["account","l10n_ve_withholding_iva","l10n_ve_fiscal_requirements","l10n_ve_imex"],
    "author" : "Thinkasoft",
    "description" : """
Fiscal Book
===============================================================================
Build all Fiscal Reports for Law in Venezuela.
Add 2 new columns because of:

Según Articulo 77 del Reglamento de la Ley del IVA No.5.363 del 12 de Julio de 1999. 
Parágrafo Segundo: El registro de las operaciones contenidas en el reporte global diario generado por las máquinas fiscales, se reflejarán en el Libro de Ventas del mismo modo que se establece respecto de los comprobantes que se emiten a no contibuyentes, indicando el número de registro de la máquina.

.. note::			
    * *El libro de ventas no contempla la sección de Ventas por cuenta de Terceros.*
""",
    "website" : "http://openerp.com.ve",
    "category" : "Generic Modules/Accounting",
    "init_xml" : [
    ],
    "demo_xml" : [
        "demo/book_base_demo.xml",
        "demo/sale_book_demo.xml",
        "demo/purchase_book_demo.xml",
    ],
    "update_xml" : [
        "wizard/fiscal_book_wizard_view.xml",
        "view/adjustment_book.xml",
        "view/fiscal_book.xml",
        "report/fiscal_book_report.xml",
        "workflow/fb_workflow.xml",
        "security/fiscal_book_security.xml",
        "security/ir.model.access.csv"
    ],
    "test": [
       # 'test/purchase.yml',
       # 'test/sale.yml',
    ],
    "active": False,
    "installable": True,
}
