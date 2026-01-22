# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AgreementSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rebate_product_id = fields.Many2one(
        string='Rebate Product',
        comodel_name='product.product',
    )
    
    @api.model
    def get_values(self):
        res = super(AgreementSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        products = ICPSudo.get_param('agreement_rebate.rebate_product_id')
        res.update(
            rebate_product_id=products
        )
        return res
    
    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].set_param('agreement_rebate.rebate_product_id', self.rebate_product_id)

class ContractSettings(models.Model):
    _inherit = 'res.company'

    rebate_product_id = fields.Many2one(
        string='Rebate Product',
        comodel_name='product.product',
    )
    journal_id = fields.Many2one(
        string='Journal',
        comodel_name='account.journal',
        ondelete='restrict',
    )
    account_id = fields.Many2one(
        string='Account',
        comodel_name='account.account',
        ondelete='restrict',
    )
    