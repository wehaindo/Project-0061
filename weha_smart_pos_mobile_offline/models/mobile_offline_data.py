from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


import logging
_logger = logging.getLogger(__name__)

class MobileOfflineData(models.Model):
    _name = 'mobile.offline.data'
    _description = 'Mobile Offline Data'

    name = fields.Datetime('Date')
    model_name = fields.Many2one('ir.model', 'Model')
    type = fields.Selection([('create','Create'),('write','Write'),('delete','Delete')], 'Type')
    data_ids = fields.Text('Data Ids')
    state = fields.Selection([('open','Ready'),('done','Synced')])
