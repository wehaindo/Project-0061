# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

import logging

_logger = logging.getLogger(__name__)

class InheritPurchaseOrder(models.Model):
    _inherit = "purchase.order"

    agreement_contract_id = fields.Many2one(
        string='Agreement Contract',
        comodel_name='agreement.contract',
        ondelete='restrict',
    )
    is_settlement = fields.Boolean(
        string='is settlement',
        default=False,
        index=True
    )
    settlement_id = fields.Many2one(
        string='settlement',
        comodel_name='settlement.process',
        ondelete='restrict',
    )

class InheritPurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _filter_product(self):
        supplier_id = self.env.context.get('default_active_id')
        _logger.info("____SUPPLIER")
        _logger.info(supplier_id)
        domain =[('id', '=', -1)]
        if supplier_id:
            domain =[('supplier_id', '=', supplier_id),('purchase_ok','=', True)]
            return domain
        return domain

    agreement_contract_id = fields.Many2one(
        string='Agreement Contract',
        comodel_name='agreement.contract',
        related='order_id.agreement_contract_id',
        readonly=True,
        store=True
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        domain=_filter_product
    )
    
    
    