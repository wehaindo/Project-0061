from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError, Warning
from dateutil.relativedelta import *
import logging

_logger = logging.getLogger(__name__)

class WizardCopyContractRebate(models.TransientModel):
    _name = "wizard.copy.contract.rebate"


    start_date = fields.Date(
        string='Rebate From',
        required=True
    )
    end_date = fields.Date(
        string='Rebate To',
        required=True
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        ondelete='set null',
    )
    is_valid = fields.Boolean("Valid", default=False)
    is_checked = fields.Boolean("Is Checked", default=False)
    copy_contract_line_ids = fields.One2many(
        string='copy contract line',
        comodel_name='wizard.copy.contract.rebate.line',
        inverse_name='copy_contract_id',
    )

    def process(self):
        from_date = self.start_date
        to_date = self.end_date
        start_date = str(from_date.year) + "-" + str(from_date.month).zfill(2) + "-" + str(from_date.day).zfill(2) + " 00:00:00"
        end_date = str(to_date.year) + "-" + str(to_date.month).zfill(2) + "-" + str(to_date.day).zfill(2) + " 23:59:59"

        args = [('create_date','>=', start_date), ('create_date','<=', end_date)]
        if self.supplier_id:
            args += [('supplier_id','=', self.supplier_id.id)]

        contract_ids = self.env['agreement.contract'].search(args)
        line = []
        supplier = 0
        for rec in contract_ids:
            if self.supplier_id:
                supplier = rec.supplier_id.id
            line.append((
                    (0,0, {'contract_id': rec.id})
                    ))
        vals = {}
        vals.update({'start_date': self.start_date})
        vals.update({'end_date': self.end_date})
        vals.update({'supplier_id': supplier})
        vals.update({'is_valid': self.is_valid})
        vals.update({'is_checked': True})
        vals.update({'copy_contract_line_ids': line})

        copy_contract_id = self.env['wizard.copy.contract.rebate'].create(vals)

        return {
            'name': 'Scan Contract Rebate',
            'res_id': copy_contract_id.id,
            'res_model': 'wizard.copy.contract.rebate',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('weha_agreement_management.view_wizard_copy_contract_rebate').id,
            'view_mode': 'form',
            'view_type': 'form',
        }

    def confirm(self):
        contract_obj = self.env['agreement.contract']
        for line in self.copy_contract_line_ids:
            contract_ids = contract_obj.search([('id','=', line.contract_id.id)])
            for rec in contract_ids:
                from_date = rec.start_date + relativedelta(years=1)
                to_date = rec.end_date + relativedelta(years=1)
                vals= {}
                vals.update({
                    'start_date': from_date,
                    'end_date': to_date,
                    'supplier_id': rec.supplier_id.id,
                    'new_supplier_id': rec.new_supplier_id.id,
                    'supplier_contract_type': rec.supplier_contract_type,
                    'supplier_sub_type': rec.supplier_sub_type,
                    'contract_holder_type': rec.contract_holder_type,
                    'supplier_source': rec.supplier_source,
                    'payment_term_id': rec.payment_term_id.id,
                    'tax_id': rec.tax_id.id,
                    'target': rec.target,
                    'description': rec.description,
                    'guarantee_min_monthly': rec.guarantee_min_monthly,
                    'guarantee_min_yearly': rec.guarantee_min_yearly,
                    'guarantee_total': rec.guarantee_total,
                    'fixed_percent': rec.fixed_percent,
                    'line_ids': rec.line_ids,
                    'branch_ids': rec.branch_ids,
                    'rebate_ids': rec.rebate_ids,
                })
                res = contract_obj.create(vals)
                _logger.info("CREATE CONTRACT")
                _logger.info(str(res.id))
                rebate = self.env['contract.rebate'].search([('contract_id','=', res.id)])
                rebate.write({'is_process': False})

        return self.open_agreement_contract()
    
    def open_agreement_contract(self):
        self.ensure_one()
        tree_view = self.env.ref("weha_agreement_management.view_agreement_contract_tree", raise_if_not_found=False)
        form_view = self.env.ref("weha_agreement_management.view_agreement_contract_form", raise_if_not_found=False)
        action = {
            "type": "ir.actions.act_window",
            "name": "Agreement Contract",
            "res_model": "agreement.contract",
            "view_mode": "tree,kanban,form,calendar,pivot,graph,activity",
            "domain": [],
        }
        if tree_view and form_view:
            action["views"] = [(tree_view.id, "tree"), (form_view.id, "form")]
        return action
    
class WizardCopyContractRebateLine(models.TransientModel):
    _name = "wizard.copy.contract.rebate.line"

    
    copy_contract_id = fields.Many2one(
        string='copy contract id',
        comodel_name='wizard.copy.contract.rebate',
        ondelete='set null',
    )
    contract_id = fields.Many2one(
        string='contract',
        comodel_name='agreement.contract',
        ondelete='set null',
    )
    supplier_id = fields.Many2one(
        string='supplier',
        comodel_name='res.partner',
        ondelete='set null',
        related='contract_id.supplier_id',
        readonly=True,
        store=True 
    )
    signature_date = fields.Date(string="Signature Date", 
        related='contract_id.signature_date',
        readonly=True,
        store=True
    )
    

    
    


