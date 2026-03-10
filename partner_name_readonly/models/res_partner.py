# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    allow_name_edit = fields.Boolean(
        string="Allow Name Edit",
        default=False,
        help="If checked, the name field can be edited. If unchecked, the name field will be readonly."
    )
