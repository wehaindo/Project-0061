# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, fields, api


class ProductTemplate(models.Model):
    """inherited product"""
    _inherit = 'product.template'

    bu_id = fields.Many2one('business.unit', string='Business Unit')
    branch_id = fields.Many2one("res.branch", string='Operating Unit')
    business_unit_ids = fields.Many2many(
        string='Business Units',
        comodel_name='business.unit',
        relation='business_unit_product_template_rel',
        column1='business_unit_id',
        column2='product_template_id',
    )
    branch_ids = fields.Many2many(
        comodel_name="res.branch",
        relation="product_templates_res_branch_rel",
        column1="res_branch_id",
        column2="product_template_id",
        string="Stores"
    )

    line_id = fields.Many2one("res.line", string='Line')
    division_id = fields.Many2one("res.division", string='Division')
    group_id = fields.Many2one("res.group", string='Group')
    dept_id = fields.Many2one("res.department", string='Department')
    sub_categ_id = fields.Many2one('product.sub.category','Product Sub Category',ondelete='set null',)
    
    @api.depends('company_id')
    def _compute_allowed_branch_ids(self):
        for po in self:
            po.allowed_branch_ids = self.env.user.branch_ids.ids
