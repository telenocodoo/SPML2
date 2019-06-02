{
    'name': 'Discount in sales, purchases and invoices',
    'description': 'Apply discount On Untaxed Amount In Invoices, Sales Orders and Purchase Orders',
    'version': '1.0.0',
    'license': 'LGPL-3',
    'category': 'Sales',
    'author': 'REZGUI Intissar',
    'website': '',
    'depends': [
        'purchase',
        'sale',
        'account',
    ],
    'data': [
        'views/purchase_order_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
    ],
    'application': True,
    'installable': True,
}
