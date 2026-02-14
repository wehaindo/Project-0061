# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Viswanth k (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    """The inherited class HrEmployee to add new fields to 'hr.employee' """
    _inherit = "hr.employee.base"

    disable_payment = fields.Boolean(
        string="POS-Disable Payment",
        help="Disable the payment button on the POS", default=True)
    disable_customer = fields.Boolean(
        string="POS-Disable Customer",
        help="Disable the customer selection button on the POS", default=True)
    disable_plus_minus = fields.Boolean(
        string="POS-Disable Plus-Minus",
        help="Disable the +/- button on the POS", default=True)
    disable_numpad = fields.Boolean(
        string="POS-Disable Numpad",
        help="Disable the number pad on the POS", default=True)
    disable_qty = fields.Boolean(
        string="POS-Disable Qty",
        help="Disable the Qty button on the POS", default=True)
    disable_discount = fields.Boolean(
        string="POS-Disable Discount",
        help="Disable the %Disc button on the POS", default=True)
    disable_price = fields.Boolean(
        string="POS-Disable price",
        help="Disable the %Price button on the POS", default=True)
    disable_remove_button = fields.Boolean(
        string="POS-Disable Remove Button",
        help="Disable the back button on the POS", default=True)
    allow_open_cash_drawer = fields.Boolean(
        string="POS-Allow Open Cash Drawer",
        help="Allow opening cash drawer from POS screen", default=False)
    
    # Fingerprint fields
    fingerprint_primary = fields.Text(
        string='Primary Fingerprint',
        help='Primary fingerprint data for employee authentication')
    fingerprint_secondary = fields.Text(
        string='Secondary Fingerprint',
        help='Secondary fingerprint data for employee authentication')
    fingerprint_primary_id = fields.Binary(
        string='Primary Fingerprint Binary',
        help='Binary data for primary fingerprint')
    fingerprint_secondary_id = fields.Binary(
        string='Secondary Fingerprint Binary',
        help='Binary data for secondary fingerprint')
