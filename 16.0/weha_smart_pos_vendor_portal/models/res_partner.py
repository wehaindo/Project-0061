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
from odoo import models, fields, api, _ 
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sharing_revenue_ids = fields.One2many('res.partner.sharing.revenue','partner_id','Sharing Revenues')


class ResPartnerSharingRevenue(models.Model):
    _name = 'res.partner.sharing.revenue'

    partner_id = fields.Many2one('res.partner','Partner #')
    name =fields.Date('Start Date')
    sharing_percentage = fields.Float('Sharing Percentage', default=0.0)
    state = fields.Selection([('active','Active'),('notactive','Not Active')],'Status', default="notactive")