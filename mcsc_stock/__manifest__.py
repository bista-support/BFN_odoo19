{
    'name': '[GECM] MCSC, LLC : METRC API',
    'summary': 'Call an endpoint with a cron job to update fields on stock.lot',
    'description': '''
        This model calls an endpoint with a cron job to update fields on stock.lot.
        This cron sould run daily and with the information received from the API, update the fields on the model.

        Developer: [gecm]
        Task ID: 2994640
        Link to project: https://www.odoo.com/web#id=2994640&cids=17&menu_id=4720&action=333&active_id=360&model=project.task&view_type=form
    ''',
    'author': 'Odoo, Inc',
    'website': 'https://www.odoo.com',
    'category': 'Inventory',
    'version': '1.1.0',
    'data': [
        'data/cron.xml',
        'data/config_parameters.xml',

        'views/stock_production_lot.xml',
    ],
    'depends': [
        'stock',
    ],
    'license': 'OPL-1',
}
