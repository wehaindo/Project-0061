
from odoo import api, fields, models, _
import base64
from dateutil.relativedelta import relativedelta

class ConsignmentSettlement(models.Model):
    _name = 'consignment.settlement'
    _description = 'Consignment Settlement'

    contract_id = fields.Many2one('consignment.contract', required=True)
    period_from = fields.Date()
    period_to = fields.Date()
    total_sales = fields.Monetary(currency_field='company_currency_id')
    total_commission = fields.Monetary(currency_field='company_currency_id')
    net_payable = fields.Monetary(currency_field='company_currency_id')
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('paid','Paid')], default='draft')
    vendor_bill_id = fields.Many2one('account.move', string='Vendor Bill')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    pdf_statement = fields.Binary(string="Settlement Statement (PDF)")
    pdf_filename = fields.Char(string="Statement Filename")

    def compute_settlement(self):
        for rec in self:
            Sales = self.env['pos.consignment.sale'].sudo().search([
                ('contract_id','=',rec.contract_id.id),
                ('create_date','>=', rec.period_from),
                ('create_date','<=', rec.period_to)
            ])
            total = sum(Sales.mapped('subtotal'))
            commission = 0.0
            for s in Sales:
                pl = self.env['consignment.contract.line'].sudo().search([('contract_id','=',rec.contract_id.id),('product_id','=',s.product_id.id)], limit=1)
                rate = pl.commission_rate if pl and pl.commission_rate else rec.contract_id.commission_value
                if rec.contract_id.commission_type == 'percent':
                    commission += s.subtotal * (rate or 0.0) / 100.0
                else:
                    commission += rate * s.qty
            rec.total_sales = total
            rec.total_commission = commission
            rec.net_payable = total - commission

    def action_confirm(self):
        for rec in self:
            rec.compute_settlement()
            bill = self.env['account.move'].sudo().create({
                'move_type': 'in_invoice',
                'partner_id': rec.contract_id.partner_id.id,
                'invoice_date': rec.period_to,
                'invoice_line_ids': [(0,0,{
                    'name': f'Consignment Settlement {rec.contract_id.name} [{rec.period_from} - {rec.period_to}]',
                    'quantity': 1,
                    'price_unit': rec.net_payable,
                })],
            })
            rec.vendor_bill_id = bill.id
            try:
                pdf, filename = rec.generate_pdf_report()
                rec.pdf_statement = base64.b64encode(pdf)
                rec.pdf_filename = filename
            except Exception:
                pass
            rec.state = 'confirmed'
            # optionally: email template send is left to configuration

    def generate_pdf_report(self):
        self.ensure_one()
        report = self.env.ref('pos_consignment.report_consignment_settlement', raise_if_not_found=True)
        pdf = report._render_qweb_pdf(self.id)[0]
        filename = 'Consignment_Settlement_%s_%s.pdf' % (self.contract_id.name, self.period_to)
        return pdf, filename

    @api.model
    def create_settlement_for_period(self, contract, date_from, date_to):
        Sales = self.env['pos.consignment.sale'].sudo().search([
            ('contract_id','=',contract.id),
            ('create_date','>=', date_from),
            ('create_date','<=', date_to)
        ])
        if not Sales:
            return None
        settlement = self.create({
            'contract_id': contract.id,
            'period_from': date_from,
            'period_to': date_to,
        })
        settlement.compute_settlement()
        return settlement

    @api.model
    def cron_generate_monthly_settlements(self):
        Contract = self.env['consignment.contract'].sudo().search([('state','=','active')])
        today = fields.Date.context_today(self)
        first_day_this_month = today.replace(day=1)
        period_to = first_day_this_month - relativedelta(days=1)
        period_from = period_to.replace(day=1)
        for contract in Contract:
            self.create_settlement_for_period(contract, period_from, period_to)
        return True
