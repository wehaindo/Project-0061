from odoo import models, fields, api, _

class ResBranch(models.Model):
    _inherit = 'res.branch'

    image_ids = fields.One2many("res.branch.display.image",'res_branch_id','Images')

class ResBranchDisplayImage(models.Model):
    _name = 'res.branch.display.image'

    res_branch_id = fields.Many2one('res.branch', 'Branch #')
    filename = fields.Char('Filename')
    filebin = fields.Binary('File', attachment=False)