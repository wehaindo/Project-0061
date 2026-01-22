# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    disable_payment_id = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='Sinergia - Deshabilitar boton pago')

    group_select_customer = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='Sinergia - Seleccion de cliente')

    group_disable_discount = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='Sinergia - Deshabilita descuentos')

    group_disable_qty = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='Sinergia - Deshabilita boton cant')

    group_disable_price = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='Sinergia - Deshabilita Btn Precio')

    group_disable_plus_minus = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='Sinergia - Deshabilita +/-')

    group_disable_numpad = fields.Many2one(
        'res.groups', compute='_compute_access_rights', string='Sinergia - Deshabilita teclado')

    def _compute_access_rights(self):
        for rec in self:
            rec.disable_payment_id = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_payment')
            rec.group_select_customer = self.env.ref(
                'sh_pos_all_in_one_retail.group_select_customer')
            rec.group_disable_discount = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_discount')
            rec.group_disable_qty = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_qty')
            rec.group_disable_price = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_price')
            rec.group_disable_plus_minus = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_plus_minus')
            rec.group_disable_numpad = self.env.ref(
                'sh_pos_all_in_one_retail.group_disable_numpad')
