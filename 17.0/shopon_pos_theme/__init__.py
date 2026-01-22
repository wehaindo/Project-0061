from . import models

from odoo import api, SUPERUSER_ID

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    asset = env['ir.asset'].search([('name', '=','shopon_pos_variables_extra_override')])
    attachment = env["ir.attachment"].search([('name', '=', 'shopon_pos_variables_extra')])
    asset.sudo().unlink()
    attachment.sudo().unlink()
