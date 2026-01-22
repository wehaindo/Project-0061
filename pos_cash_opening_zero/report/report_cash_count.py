from odoo import api, models

class ReporCashCount(models.AbstractModel):
    _name = 'report.pos_cash_opening_zero.report_cash_count'

    @api.model
    def _get_report_values(self, ids, data=None):
        cash_count_id = self.env['pos.cash.count'].browse(ids)
        args = {
            'doc_ids': ids,
            'doc_model': 'pos.cash.count',
            'docs': cash_count_id,
            'report_type': data.get('report_type') if data else '',
        }
        return args
