from odoo import _, api, fields, models, tools

class SmartPosNote(models.Model):
    _name = 'smart.pos.note'

    name = fields.Char('Name', size=200, required=True)    
