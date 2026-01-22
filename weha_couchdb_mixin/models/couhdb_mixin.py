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
import logging

_logger = logging.getLogger(__name__)


class CouchDBMixin(models.AbstractModel):
    _name = 'couch.db.mixin'


    def sync(self, vals):
        pass

    def create(self, vals):
        res = super(CouchDBMixin,self).create(vals)
