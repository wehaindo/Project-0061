# -*- coding: utf-8 -*-
#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

import logging
from odoo import models, fields


_logger = logging.getLogger(__name__)


class Branch(models.Model):
    """res branch"""
    _name = "res.branch"
    _description = 'Company Branches'
    _order = 'name'

    name = fields.Char(string='Branch', required=True, store=True)
    code = fields.Char('Code', required=True)
    company_id = fields.Many2one('res.company', required=True, string='Company')
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state',string="Fed. State", domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country',  string="Country")
    email = fields.Char(store=True, )
    phone = fields.Char(store=True)
    website = fields.Char(readonly=False)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The Branch name must be unique !')
    ]

    #Customer Display Adv
    image_ids = fields.One2many("res.branch.display.image",'branch_id','Images')

class ResBranchDisplayImage(models.Model):
    _name = 'res.branch.display.image'

    branch_id = fields.Many2one('res.branch', 'Branch #')
    filename = fields.Char('Filename')
    filebin = fields.Binary('File', attachment=False)