import json
import logging
from datetime import date, timedelta
import requests
from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class ProductionLot(models.Model):
    _inherit = 'stock.lot'

    last_update_metrc = fields.Datetime('Last Update METRC', readonly=True)
    metrc_qty = fields.Float('METRC Quantity', readonly=True)
    metrc_id = fields.Char('METRC ID')
    metrc_product_name = fields.Char('METRC Product Name', readonly=True)
    metrc_unit_of_measure = fields.Char(
        'METRC Unit of Measure Name', readonly=True)
    qty_difference = fields.Float(
        'Quantity Difference', compute='_compute_qty_difference', store=True)

    @api.depends('product_qty', 'metrc_qty')
    def _compute_qty_difference(self):
        for lot in self:
            lot.qty_difference = lot.metrc_qty - lot.product_qty

    def cron_call_endpoint(self):
        session = requests.Session()
        headers = {
            'Authorization': self.env['ir.config_parameter'].sudo().get_param('auth_token'),
        }

        license_numbers = self.env['ir.config_parameter'].sudo(
        ).get_param('licenseNumber').split(',')
        for license_number in license_numbers:
            daycount = 0
            while (daycount < 365):
                response = session.get('http://api-co.metrc.com/packages/v1/active', params={
                                       "licenseNumber": license_number, "lastModifiedStart": date.today() - timedelta(daycount+1), "lastModifiedEnd": date.today() - timedelta(daycount)}, headers=headers)

                try:
                    response.raise_for_status()
                    response_dict = json.loads(response.text)
                    assert type(response_dict) == list
                except Exception as e:
                    _logger.error('Error on call to API: ', e)

                self._update_metrc_values(response_dict)
                daycount += 1

    def _update_metrc_values(self, response_dict):
        for item in response_dict:
            lot = self.search([('metrc_id', '=', item['Label'])], limit=1)
            check_item_keys = all(key in item for key in (
                'Item', 'Quantity', 'UnitOfMeasureName'))
            if lot and check_item_keys:
                lot.write({
                    'metrc_qty': item['Quantity'],
                    'metrc_product_name': item['Item']['Name'],
                    'metrc_unit_of_measure': item['UnitOfMeasureName'],
                    'last_update_metrc': fields.Datetime.now(),
                })
            else:
                _logger.warning('METRC ID %s not found in Odoo', item['Label'])
