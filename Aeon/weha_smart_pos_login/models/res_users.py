from datetime import datetime
from uuid import uuid4
import pytz

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError

class ResUsers(models.Model):
    _inherit = 'res.users'

    rfid = fields.Char('RFID', size=255)