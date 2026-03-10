{
    'name': 'Purchase Order Warehouse Address Report',
    'version': '19.0.1.0.0',
    'summary': 'Customize PO report to show Warehouse address in Ship To',
    'category': 'Purchases',
    'author': 'Your Company',
    'depends': ['purchase', 'stock'],
    'data': [
        'views/purchase_report.xml',
        'views/delivery_slip_report.xml',
    ],
    'installable': True,
    'application': False,
}