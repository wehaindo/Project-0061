from odoo import models, fields, api, _ 



class WehaContact(models.Model):
    _name = 'weha.contact'

    name = fields.Char('Name', size=250)
    email = fields.Char('Email', size=250)

