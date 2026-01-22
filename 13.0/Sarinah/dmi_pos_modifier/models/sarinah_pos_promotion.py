
# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime

class SarinahPosPromotion(models.Model):
    _inherit = 'srn.pos.product.discount'

    available_in_receipt = fields.Boolean(string="Available in Receipt", default=False)
    date_to = fields.Date(string="Date To")
    date_from = fields.Date(string="Date From")
    terms_text = fields.Text(string="Terms & Conditions")
    type_scan = fields.Selection(selection=[('QR', 'QR'), ('barcode', 'Barcode')], string="Type Scan", default='QR')
    min_amount_show = fields.Float(string="Minimum Amount Receipt", default=0.0)
    max_amount_show = fields.Float(string="Maximum Amount Receipt", default=9999999.0)
    start_date = fields.Datetime(string="Start Date")
    end_date = fields.Datetime(string="End Date")
    pos_config_ids = fields.Many2many('pos.config', string='POS Config')

    day_of_week_ids = fields.Many2many('day.week', string="Day Of The Week", required=True)

    def compute_all_day_of_week_ids(self):
        for res in self :
            res.day_of_week_ids = [(6, 0, [x.id for x in self.env['day.week'].search([])])]

    @api.model
    def default_get(self, fields):
        res = super(SarinahPosPromotion, self).default_get(fields)
        ids = self.env['day.week'].search([])
        res.update({'day_of_week_ids': [(6, 0, [x.id for x in ids])]})
        return res

    def write(self, vals):
        res = super(SarinahPosPromotion, self).write(vals)
        self.validation_check_single_available_in_receipt()
        return res

    @api.model
    def create(self, vals):
        rec = super(SarinahPosPromotion, self).create(vals)
        rec.validation_check_single_available_in_receipt()
        return rec

    def validation_check_single_available_in_receipt(self):
        for record in self:
            if record.available_in_receipt:

                if record.min_amount_show > record.max_amount_show or record.max_amount_show < record.min_amount_show:
                    raise ValidationError("Promotion ranges amount wrong.")
                # Cari promosi lain yang memiliki available_in_receipt = True
                other_records = self.search([
                    ('id', '!=', record.id),
                    ('available_in_receipt', '=', True)
                ])
                for promo in other_records:
                    for pos_config in record.pos_config_ids:
                        if pos_config in promo.pos_config_ids:
                            # Cek apakah rentangnya overlap
                            if not (record.min_amount_show > promo.max_amount_show or record.max_amount_show < promo.min_amount_show):
                                raise ValidationError("Promotion ranges amount cannot overlap in the same POS configuration.")

    @api.constrains('available_in_receipt')
    def _check_single_available_in_receipt(self):
        for record in self:
            if record.available_in_receipt:
                # Cari promosi lain yang memiliki available_in_receipt = True
                other_records = self.search([
                    ('id', '!=', record.id),
                    ('available_in_receipt', '=', True)
                ])

                if record.min_amount_show > record.max_amount_show or record.max_amount_show < record.min_amount_show:
                    raise ValidationError("Promotion ranges amount wrong.")

                for promo in other_records:
                    for pos_config in record.pos_config_ids:
                        if pos_config in promo.pos_config_ids:
                            # Cek apakah rentangnya overlap
                            if not (record.min_amount_show > promo.max_amount_show or record.max_amount_show < promo.min_amount_show):
                                raise ValidationError("Promotion ranges amount cannot overlap in the same POS configuration.")

    @api.model
    def _get_expired_promotions(self):
        current_datetime = datetime.now()

        # Search for expired promotions where:
        # - 'start_date' is not empty (not None)
        # - 'end_date' is not empty (not None)
        # - 'current_datetime' is outside of 'start_date' and 'end_date'
        expired_promotions = self.search([
            ('active', '=', True),  # The promotion is active
            ('start_date', '!=', False),  # Ensure start_date is set
            ('end_date', '!=', False),  # Ensure end_date is set
            ('start_date', '<', current_datetime),  # Start date is before current time
            ('end_date', '<', current_datetime)  # End date is before current time
        ])

        # Deactivate expired promotions
        expired_promotions.write({'active': False})

        # Search for promotions that are still valid (current date is within start_date and end_date)
        valid_promotions = self.search([
            ('active', '=', False),  # The promotion is not active
            ('start_date', '!=', False),  # Ensure start_date is set
            ('end_date', '!=', False),  # Ensure end_date is set
            ('start_date', '<', current_datetime),  # Start date is before current time
            ('end_date', '>=', current_datetime)  # End date is after or on current time
        ])

        # Activate valid promotions (promotions that are still within the date range)
        valid_promotions.write({'active': True})
