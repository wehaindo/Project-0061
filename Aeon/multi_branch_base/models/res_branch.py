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

import logging
_logger = logging.getLogger(__name__)


class Branch(models.Model):
    """res branch"""
    _name = "res.branch"
    _description = 'Company Branches'
    _order = 'name'

    def name_get(self):
        result = []            
        for rec in self:
            result.append((rec.id, '(%s) %s' % (rec.code,rec.name)))
        return result
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = list(args or [])
        # optimize out the default criterion of ``ilike ''`` that matches everything
        if not (name == '' and operator == 'ilike'):
            args += ['|', (self._rec_name, operator, name), ('code', operator, name)]
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)

    name = fields.Char(string='Store', required=True, store=True)  
    color = fields.Integer()
    code = fields.Char(string='Code', size=20)
    company_id = fields.Many2one('res.company', required=True, string='Company')
    business_unit_id = fields.Many2one('business.unit', required=True, string='Business Unit')
    
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', string="Fed. State", domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country',  string="Country")
    email = fields.Char(store=True, )
    phone = fields.Char(store=True)
    website = fields.Char(readonly=False)
    supplier_ids = fields.Many2many(string='Supplier Branch',comodel_name='res.partner',domain="[('bu_id', '=', business_unit_id)]")
    couchdb_server_url = fields.Char('CouchDB Server')
    couchdb_name = fields.Char('CouchDB Name')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Branch name must be unique !')
    ]
