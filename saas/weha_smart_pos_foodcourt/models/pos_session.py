# -*- coding: utf-8 -*-
#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from collections import defaultdict
from odoo import models, fields, api
from odoo.tools import float_is_zero, float_round
from odoo.exceptions import UserError, ValidationError


import logging
_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _get_split_receivable_vals(self, payment, amount, amount_converted):
        partial_vals = {
            'account_id': payment.payment_method_id.receivable_account_id.id,
            'move_id': self.move_id.id,
            'partner_id': self.env["res.partner"]._find_accounting_partner(payment.partner_id).id,
            'name': '%s - %s' % (self.name, payment.payment_method_id.name),
        }
        if payment.payment_method_id.allow_for_wallet:
            partial_vals.update({
                'account_id': self.config_id.deposit_account_id.id,
                'is_deposit': True
            })

        return self._debit_amounts(partial_vals, amount, amount_converted)

    def _get_combine_receivable_vals(self, payment_method, amount, amount_converted):
        partial_vals = {
            'account_id': payment_method.receivable_account_id.id,
            'move_id': self.move_id.id,
            'name': '%s - %s' % (self.name, payment_method.name)
        }
        return self._debit_amounts(partial_vals, amount, amount_converted)

    def _accumulate_amounts(self, data):
        amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0}
        tax_amounts = lambda: {'amount': 0.0, 'amount_converted': 0.0, 'base_amount': 0.0, 'base_amount_converted': 0.0}
        split_receivables = defaultdict(amounts)
        split_receivables_cash = defaultdict(amounts)
        combine_receivables = defaultdict(amounts)
        combine_receivables_cash = defaultdict(amounts)
        invoice_receivables = defaultdict(amounts)
        sales = defaultdict(amounts)
        taxes = defaultdict(tax_amounts)
        stock_expense = defaultdict(amounts)
        stock_return = defaultdict(amounts)
        stock_output = defaultdict(amounts)
        deposit_vals = []
        rounding_difference = {'amount': 0.0, 'amount_converted': 0.0}
        wallet_difference = {'amount': 0.0, 'amount_converted': 0.0}
        # Track the receivable lines of the invoiced orders' account moves for reconciliation
        # These receivable lines are reconciled to the corresponding invoice receivable lines
        # of this session's move_id.
        order_account_move_receivable_lines = defaultdict(lambda: self.env['account.move.line'])
        rounded_globally = self.company_id.tax_calculation_rounding_method == 'round_globally'
        for order in self.order_ids:
            # Combine pos receivable lines
            # Separate cash payments for cash reconciliation later.
            for payment in order.payment_ids:
                amount, date = payment.amount, payment.payment_date
                if payment.payment_method_id.split_transactions:
                    if payment.payment_method_id.is_cash_count:
                        split_receivables_cash[payment] = self._update_amounts(split_receivables_cash[payment],
                                                                               {'amount': amount}, date)
                    else:
                        split_receivables[payment] = self._update_amounts(split_receivables[payment],
                                                                          {'amount': amount}, date)
                else:
                    key = payment.payment_method_id
                    if payment.payment_method_id.is_cash_count:
                        combine_receivables_cash[key] = self._update_amounts(combine_receivables_cash[key],
                                                                             {'amount': amount}, date)
                    else:
                        combine_receivables[key] = self._update_amounts(combine_receivables[key], {'amount': amount},
                                                                        date)

            if order.is_invoiced:
                # Combine invoice receivable lines
                key = order.partner_id.property_account_receivable_id.id
                if self.config_id.cash_rounding:
                    invoice_receivables[key] = self._update_amounts(invoice_receivables[key],
                                                                    {'amount': order.amount_paid}, order.date_order)
                else:
                    invoice_receivables[key] = self._update_amounts(invoice_receivables[key],
                                                                    {'amount': order.amount_total}, order.date_order)
                # side loop to gather receivable lines by account for reconciliation
                for move_line in order.account_move.line_ids.filtered(
                        lambda aml: aml.account_id.internal_type == 'receivable' and not aml.reconciled):
                    order_account_move_receivable_lines[move_line.account_id.id] |= move_line
            else:
                order_taxes = defaultdict(tax_amounts)
                for order_line in order.lines:
                    if self.config_id.enable_wallet and (order_line.product_id.id == self.config_id.wallet_product.id):
                        amount = order_line.price_subtotal_incl
                        amount_converted = self.company_id.currency_id.round(order_line.price_subtotal_incl)
                        deposit_vals.append(self._get_deposit_credit_vals(amount, amount_converted, order_line.order_id))
                    else:
                        line = self._prepare_line(order_line)
                        sale_key = (
                            line['income_account_id'],
                            -1 if line['amount'] < 0 else 1,
                            tuple((tax['id'], tax['account_id'], tax['tax_repartition_line_id']) for tax in
                                  line['taxes']),
                            line['base_tags'],
                        )
                        sales[sale_key] = self._update_amounts(sales[sale_key], {'amount': line['amount']},
                                                               line['date_order'])
                        # Combine tax lines
                        for tax in line['taxes']:
                            tax_key = (
                            tax['account_id'], tax['tax_repartition_line_id'], tax['id'], tuple(tax['tag_ids']))
                            order_taxes[tax_key] = self._update_amounts(
                                order_taxes[tax_key],
                                {'amount': tax['amount'], 'base_amount': tax['base']},
                                tax['date_order'],
                                round=not rounded_globally
                            )
                for tax_key, amounts in order_taxes.items():
                    if rounded_globally:
                        amounts = self._round_amounts(amounts)
                    for amount_key, amount in amounts.items():
                        taxes[tax_key][amount_key] += amount

                if self.company_id.anglo_saxon_accounting and order.picking_ids.ids:
                    # Combine stock lines
                    stock_moves = self.env['stock.move'].search([
                        ('picking_id', 'in', order.picking_ids.ids),
                        ('company_id.anglo_saxon_accounting', '=', True),
                        ('product_id.categ_id.property_valuation', '=', 'real_time')
                    ])
                    for move in stock_moves:
                        exp_key = move.product_id._get_product_accounts()['expense']
                        out_key = move.product_id.categ_id.property_stock_account_output_categ_id
                        amount = -sum(move.sudo().stock_valuation_layer_ids.mapped('value'))
                        stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount},
                                                                      move.picking_id.date, force_company_currency=True)
                        if move.location_id.usage == 'customer':
                            stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount},
                                                                         move.picking_id.date,
                                                                         force_company_currency=True)
                        else:
                            stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount},
                                                                         move.picking_id.date,
                                                                         force_company_currency=True)

                if order.change_amount_for_deposit > self.company_id.currency_id.round(0.0):
                    # wallet_amount['amount'] = order.change_amount_for_wallet
                    deposit_difference = self._update_amounts(deposit_difference,
                                                             {'amount': order.change_amount_for_deposit},
                                                             order.date_order)
                    deposit_difference['order_id'] = order

                if self.config_id.cash_rounding:
                    diff = order.amount_paid - order.amount_total - order.change_amount_for_deposit
                    rounding_difference = self._update_amounts(rounding_difference, {'amount': diff}, order.date_order)
                # Increasing current partner's customer_rank
                order.partner_id._increase_rank('customer_rank')

        if self.company_id.anglo_saxon_accounting:
            global_session_pickings = self.picking_ids.filtered(lambda p: not p.pos_order_id)
            if global_session_pickings:
                stock_moves = self.env['stock.move'].search([
                    ('picking_id', 'in', global_session_pickings.ids),
                    ('company_id.anglo_saxon_accounting', '=', True),
                    ('product_id.categ_id.property_valuation', '=', 'real_time'),
                ])
                for move in stock_moves:
                    exp_key = move.product_id._get_product_accounts()['expense']
                    out_key = move.product_id.categ_id.property_stock_account_output_categ_id
                    amount = -sum(move.stock_valuation_layer_ids.mapped('value'))
                    stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount},
                                                                  move.picking_id.date)
                    if move.location_id.usage == 'customer':
                        stock_return[out_key] = self._update_amounts(stock_return[out_key], {'amount': amount},
                                                                     move.picking_id.date)
                    else:
                        stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount},
                                                                     move.picking_id.date)
        MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)
        MoveLine.create(deposit_vals)
        data.update({
            'taxes': taxes,
            'sales': sales,
            'stock_expense': stock_expense,
            'split_receivables': split_receivables,
            'combine_receivables': combine_receivables,
            'split_receivables_cash': split_receivables_cash,
            'combine_receivables_cash': combine_receivables_cash,
            'invoice_receivables': invoice_receivables,
            'stock_return': stock_return,
            'stock_output': stock_output,
            'order_account_move_receivable_lines': order_account_move_receivable_lines,
            'rounding_difference': rounding_difference,
            'wallet_difference': wallet_difference,
            'MoveLine': MoveLine
        })
        return data

    def _get_deposit_credit_vals(self, amount, amount_converted, order):
        partial_args = {
            'name': 'Wallet Credit',
            'is_wallet': True,
            'move_id': self.move_id.id,
            'partner_id': order.partner_id._find_accounting_partner(order.partner_id).id,
            'account_id': self.config_id.wallet_account_id.id,
        }
        return self._credit_amounts(partial_args, amount, amount_converted)

    def _create_non_reconciliable_move_lines(self, data):
        # Create account.move.line records for
        #   - sales
        #   - taxes
        #   - stock expense
        #   - non-cash split receivables (not for automatic reconciliation)
        #   - non-cash combine receivables (not for automatic reconciliation)
        taxes = data.get('taxes')
        sales = data.get('sales')
        stock_expense = data.get('stock_expense')
        split_receivables = data.get('split_receivables')
        combine_receivables = data.get('combine_receivables')
        rounding_difference = data.get('rounding_difference')
        wallet_difference = data.get('wallet_difference')
        MoveLine = data.get('MoveLine')

        tax_vals = [
            self._get_tax_vals(key, amounts['amount'], amounts['amount_converted'], amounts['base_amount_converted'])
            for key, amounts in taxes.items() if amounts['amount']]
        # Check if all taxes lines have account_id assigned. If not, there are repartition lines of the tax that have no account_id.
        tax_names_no_account = [line['name'] for line in tax_vals if line['account_id'] == False]
        if len(tax_names_no_account) > 0:
            error_message = _(
                'Unable to close and validate the session.\n'
                'Please set corresponding tax account in each repartition line of the following taxes: \n%s'
            ) % ', '.join(tax_names_no_account)
            raise UserError(error_message)
        rounding_vals = []
        deposit_vals = []

        if not float_is_zero(rounding_difference['amount'],
                             precision_rounding=self.currency_id.rounding) or not float_is_zero(
                rounding_difference['amount_converted'], precision_rounding=self.currency_id.rounding):
            rounding_vals = [self._get_rounding_difference_vals(rounding_difference['amount'],
                                                                rounding_difference['amount_converted'])]
        if not float_is_zero(wallet_difference['amount'],
                             precision_rounding=self.currency_id.rounding) or not float_is_zero(
                wallet_difference['amount_converted'], precision_rounding=self.currency_id.rounding):
            deposit_vals = [self._get_deposit_difference_vals(wallet_difference['order_id'], wallet_difference['amount'],
                                                            wallet_difference['amount_converted'])]

        MoveLine.create(
            tax_vals
            + [self._get_sale_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in
               sales.items()]
            + [self._get_stock_expense_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in
               stock_expense.items()]
            + [self._get_split_receivable_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in
               split_receivables.items()]
            + [self._get_combine_receivable_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts
               in combine_receivables.items()]
            + rounding_vals
            + deposit_vals
        )
        return data

    def _get_deposit_difference_vals(self, order, amount, amount_converted):
        if self.config_id.enable_deposit:
            partial_args = {
                'name': 'Wallet Credit',
                'is_wallet': True,
                'move_id': self.move_id.id,
                'partner_id': order.partner_id._find_accounting_partner(order.partner_id).id,
                'account_id': self.config_id.wallet_account_id.id,
            }
            return self._credit_amounts(partial_args, amount, amount_converted)
