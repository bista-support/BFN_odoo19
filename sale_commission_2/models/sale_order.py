# Copyright 2014-2022 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime, timedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends("order_line.agent_ids.amount")
    def _compute_commission_total(self):
        for record in self:
            record.commission_total = sum(record.mapped("order_line.agent_ids.amount"))

    commission_total = fields.Float(
        string="Commissions",
        compute="_compute_commission_total",
        store=True,
    )

    partner_agent_ids = fields.Many2many(
        string="Agents",
        comodel_name="res.partner",
        compute="_compute_agents",
        search="_search_agents",
    )


    sale_agent_id = fields.Many2one("res.partner", string="Sales Agent")
    pm_agent_ids = fields.Many2one("res.partner",string="Sales Manager")#when go live emove this field.
    pm_agent_id = fields.Many2one("res.partner",string="Sales Manager")
    commission_paid = fields.Boolean(string="Commission Paid")
    commission_paid_date = fields.Datetime(string="Paid Date")
    has_invoice_lines = fields.Boolean(
        string="Has Invoice Lines",
        compute="_compute_has_invoice_lines",
        store=False,
    )

    @api.depends("invoice_ids")
    def _compute_has_invoice_lines(self):
        for record in self:
            record.has_invoice_lines = bool(record.invoice_ids)





    @api.model
    def create(self, vals):
        # Set pm_agent_id from settings if not already set
        if not vals.get('pm_agent_id'):
            default_agent_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_partner_id')
            if default_agent_id:
                vals['pm_agent_id'] = int(default_agent_id)

        # Set sale_agent_id from user_id if not already set
        if not vals.get('sale_agent_id') and vals.get('user_id'):
            user = self.env['res.users'].browse(vals['user_id'])
            if user and user.partner_id:
                vals['sale_agent_id'] = user.partner_id.id

        return super().create(vals)

    def write(self, vals):
        for order in self:
            if not order.pm_agent_id and not vals.get('pm_agent_id'):
                default_agent_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_partner_id')
                if default_agent_id:
                    vals['pm_agent_id'] = int(default_agent_id)
        return super(SaleOrder, self).write(vals)



    @api.depends("partner_agent_ids", "order_line.agent_ids.agent_id")
    def _compute_agents(self):
        for so in self:
            so.partner_agent_ids = [
                (6, 0, so.mapped("order_line.agent_ids.agent_id").ids)
            ]

    @api.model
    def _search_agents(self, operator, value):
        sol_agents = self.env["sale.order.line.agent"].search(
            [("agent_id", operator, value)]
        )
        return [("id", "in", sol_agents.mapped("object_id.order_id").ids)]

    def recompute_lines_agents(self):
        self.mapped("order_line").recompute_agents()

    def recompute_lines_agents_amount(self):
        self.mapped("order_line").agent_ids._compute_amount()


class SaleOrderLine(models.Model):
    _inherit = [
        "sale.order.line",
        "commission.mixin",
    ]
    _name = "sale.order.line"

    agent_ids = fields.One2many(comodel_name="sale.order.line.agent")

    is_service_product = fields.Boolean(
        string='Is Service Product',
        compute='_compute_is_service_product',
        store=True,
    )
    
    has_invoice_lines = fields.Boolean(
        string="Has Invoice Lines",
        related="order_id.has_invoice_lines",
        store=False,
        readonly=True,
    )

    @api.depends('product_id.type')
    def _compute_is_service_product(self):
        for line in self:
            line.is_service_product = line.product_id.type == 'service'


    @api.depends("order_id.sale_agent_id", "order_id.pm_agent_id", "order_id.partner_id", "commission_free")
    def _compute_agent_ids(self):
        for record in self:
            record.agent_ids = False
            if record.commission_free:
                continue

            agents = []
            # Add main partner's agents
            if record.order_id.partner_id:
                agents += record.order_id.partner_id.agent_ids.filtered(lambda a: not a.commission_id.settlement_type or a.commission_id.settlement_type == "sale_invoice")
            # Add sale_agent_id and pm_agent_id if set
            if record.order_id.sale_agent_id:
                agents.append(record.order_id.sale_agent_id)
            if record.order_id.pm_agent_id:
                agents.append(record.order_id.pm_agent_id)

            # Remove duplicates if any
            agents = list(set(agents))

            record.agent_ids = [(0, 0, record._prepare_agent_vals(agent)) for agent in agents]

    def _prepare_invoice_line(self, **optional_values):
        vals = super()._prepare_invoice_line(**optional_values)
        vals["agent_ids"] = [
            (0, 0, {"agent_id": x.agent_id.id, "commission_id": x.commission_id.id})
            for x in self.agent_ids
        ]
        return vals






class SaleOrderLineAgent(models.Model):
    _inherit = "commission.line.mixin"
    _name = "sale.order.line.agent"
    _description = "Agent detail of commission line in order lines"

    object_id = fields.Many2one(comodel_name="sale.order.line")

    @api.depends(
        "commission_id",
        "object_id.price_subtotal",
        "object_id.product_id",
        "object_id.product_uom_qty",
    )
    def _compute_amount(self):
        for line in self:
            order_line = line.object_id
            line.amount = line._get_commission_amount(
                line.commission_id,
                order_line.price_subtotal,
                order_line.product_id,
                order_line.product_uom_qty,
            )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    my_partner_id = fields.Many2one(
        'res.partner',
        string='Sales Manager',
        config_parameter='sale.default_partner_id'
    )
