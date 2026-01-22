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

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_interface = fields.Boolean('Enable Interface', default=False)    
    interface_type = fields.Selection([('electron','Electron'),('android','Android')],'Interface Type', default="electron")
    interface_printer_ip = fields.Char(string='Interface Printer IP', help="Local IP address of an Interface receipt printer.")
    interface_printer_port = fields.Char(string='Interface Printer Port', help="Local IP address of an Interface receipt printer.")

    