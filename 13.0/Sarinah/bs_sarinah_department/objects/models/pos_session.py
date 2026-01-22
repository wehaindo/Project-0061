from collections import defaultdict
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _prepare_line(self, order_line):
        _logger.info('Start _prepare_line')
        res = super(PosSession, self)._prepare_line(order_line)
        if order_line.product_id.name != "No Change": 
            if order_line.product_id.is_consignment:
                account = order_line.order_id.config_id.department_id.account_income_consign_id
                if account:
                    res.update({'income_account_id': account.id})
            else:
                # Edited by LLHa
                if not order_line.product_id.coupon:
                    sku = order_line.product_id.default_code[0:5] if order_line.product_id.default_code is not None else '' # add by yayat untuk discount with product
                    _logger.info('\n ############ %s', sku)
                    if order_line.product_id.default_code[0:5] not in ["ZPTS","DCDWP","ADMFE"]:  # use to except product with default code, DCDWP add by yayat for discount with product and pos admin fee, income account ambil dari product
                                                                        # that use specific account
                                                                        # (not the one that set on department of POS)
                    # !Edited by LLHa
                        account = order_line.order_id.config_id.department_id.account_income_depart_id
                        if account:
                            res.update({'income_account_id': account.id})
        _logger.info('End _prepare_line')
        return res

    def _accumulate_amounts(self, data):
        # Accumulate the amounts for each accounting lines group
        # Each dict maps `key` -> `amounts`, where `key` is the group key.
        # E.g. `combine_receivables` is derived from pos.payment records
        # in the self.order_ids with group key of the `payment_method_id`
        # field of the pos.payment record.
        _logger.info('Start _accumulate_amounts')
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
        stock_output = defaultdict(amounts)
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
                        split_receivables_cash[payment] = self._update_amounts(split_receivables_cash[payment], {'amount': amount}, date)
                    else:
                        split_receivables[payment] = self._update_amounts(split_receivables[payment], {'amount': amount}, date)
                else:
                    key = payment.payment_method_id
                    if payment.payment_method_id.is_cash_count:
                        combine_receivables_cash[key] = self._update_amounts(combine_receivables_cash[key], {'amount': amount}, date)
                    else:
                        combine_receivables[key] = self._update_amounts(combine_receivables[key], {'amount': amount}, date)

            if order.is_invoiced:
                # Combine invoice receivable lines
                key = order.partner_id
                invoice_receivables[key] = self._update_amounts(invoice_receivables[key], {'amount': order._get_amount_receivable()}, order.date_order)
                # side loop to gather receivable lines by account for reconciliation
                for move_line in order.account_move.line_ids.filtered(lambda aml: aml.account_id.internal_type == 'receivable' and not aml.reconciled):
                    order_account_move_receivable_lines[move_line.account_id.id] |= move_line
            else:
                order_taxes = defaultdict(tax_amounts)
                for order_line in order.lines:
                    line = self._prepare_line(order_line)
                    # Combine sales/refund lines
                    sale_key = (
                        # account
                        line['income_account_id'],
                        # sign
                        -1 if line['amount'] < 0 else 1,
                        # for taxes
                        tuple((tax['id'], tax['account_id'], tax['tax_repartition_line_id']) for tax in line['taxes']),
                        line['base_tags'],
                    )
                    sales[sale_key] = self._update_amounts(sales[sale_key], {'amount': line['amount']}, line['date_order'])
                    # Combine tax lines
                    for tax in line['taxes']:
                        tax_key = (tax['account_id'], tax['tax_repartition_line_id'], tax['id'], tuple(tax['tag_ids']))
                        order_taxes[tax_key] = self._update_amounts(
                            order_taxes[tax_key],
                            {'amount': tax['amount'], 'base_amount': tax['base']},
                            tax['date_order'],
                            round=not rounded_globally
                        )
                _logger.info('Start _tax_key')
                for tax_key, amounts in order_taxes.items():
                    if rounded_globally:
                        amounts = self._round_amounts(amounts)
                    for amount_key, amount in amounts.items():
                        taxes[tax_key][amount_key] += amount
                _logger.info('End _tax_key')
                
                _logger.info('Start _anglo')
                if self.company_id.anglo_saxon_accounting and order.picking_id.id:
                    # Combine stock lines
                    _logger.info('Start _order_pickings')
                    order_pickings = self.env['stock.picking'].search([
                        '|',
                        ('origin', '=', '%s - %s' % (self.name, order.name)),
                        ('id', '=', order.picking_id.id)
                    ])
                    _logger.info('Enx _order_pickings')
                    _logger.info('Start _stock_moves')
                    # stock_moves = self.env['stock.move'].search([
                    #     ('picking_id', 'in', order_pickings.ids),
                    #     ('company_id.anglo_saxon_accounting', '=', True),
                    #     ('product_id.categ_id.property_valuation', '=', 'real_time')
                    # ])                   
                    stock_moves = self.env['stock.move'].search([
                        ('picking_id', 'in', order_pickings.ids)
                    ])

                    # Filter in Python (faster than ORM joins on large data)
                    stock_moves = stock_moves.filtered(
                        lambda m: m.company_id.anglo_saxon_accounting and
                                m.product_id.categ_id.property_valuation == 'real_time'
                    )
                    _logger.info('End _stock_moves')
                    _logger.info('Start loop _stock_moves')
                    for move in stock_moves:
                        _logger.info('Start in loop _stock_moves')
                        # get expense and stock output account from department
                        if move.product_id.name != "No Change":
                            if move.product_id.is_consignment:
                                output_account = self.config_id.department_id.account_expense_consign_id
                                account = self.config_id.department_id.account_stock_output_consign_id
                            else:
                                # Edited by LLHa
                                if not move.product_id.coupon:
                                    account = None
                                else:
                                # !Edited by LLHa
                                    account = move.product_id.categ_id.property_stock_account_output_categ_id

                                output_account = move.product_id.categ_id.property_stock_account_output_categ_id
                        _logger.info('Start in loop _exp_key')
                        exp_key = account or move.product_id.property_account_expense_id or move.product_id.categ_id.property_account_expense_categ_id
                        _logger.info('End in loop _exp_key')
                        _logger.info('Start in loop _out_key')
                        out_key = output_account or move.product_id.categ_id.property_stock_account_output_categ_id
                        _logger.info('End in loop _out_key')
                        _logger.info('Start in loop _amount')
                        amount = -sum(move.sudo().stock_valuation_layer_ids.mapped('value'))
                        _logger.info('End in loop _amount')
                        
                        if move.product_id.name != "No Change":
                            _logger.info('Start in loop _no_change_2')
                            if move.product_id.is_consignment:
                                _logger.info('Start in loop _vendor_product')
                                vendor_product = self.env['vendor.product.variant'].sudo().search([('product_id', '=', move.product_id.id)], limit=1)
                                _logger.info('End in loop _vendor_product')
                                
                                if vendor_product:                         
                                    _logger.info('Start in loop _margin_1')           
                                    margin = vendor_product.margin_percentage
                                    _logger.info('End in loop _margin_1')           
                                else:
                                    _logger.info('Start in loop _margin_2')           
                                    margin = move.product_id.owner_id.consignment_margin
                                    _logger.info('End in loop _margin_2')           
                                _logger.info('Start in loop _orderlines')
                                orderlines = order.lines.filtered(lambda l: l.product_id == move.product_id)
                                _logger.info('End in loop _orderlines')
                                # EDITED : 22 Februari 2022
                                # price = sum(orderlines.mapped('price_subtotal')) / sum(orderlines.mapped('qty')) * ((100 - margin ) / 100)
                                try:
                                    _logger.info('Start in loop _price')
                                    price = sum(orderlines.mapped('price_subtotal')) / sum(orderlines.mapped('qty')) * ((100 - margin ) / 100)
                                    _logger.info('End in loop _price')
                                except ZeroDivisionError:
                                    price = 0
                                    
                                _logger.info('Start in loop _amount')                                
                                amount = -price * move.quantity_done                                
                                _logger.info('Amount')
                                _logger.info(amount)
                                _logger.info('End in loop _amount')
                            _logger.info('End in loop _no_change_2')
                                                    
                        _logger.info('Start in loop _stock_expense')
                        stock_expense[exp_key] = self._update_amounts(stock_expense[exp_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
                        _logger.info('End in loop _stock_expense')
                        _logger.info('Start in loop _stock_output')
                        stock_output[out_key] = self._update_amounts(stock_output[out_key], {'amount': amount}, move.picking_id.date, force_company_currency=True)
                        _logger.info('End in loop _stock_output')
                        
                        _logger.info('End in loop _stock_moves')        
                    _logger.info('End loop _stock_moves')    
                # Increasing current partner's customer_rank
                partners = (order.partner_id | order.partner_id.commercial_partner_id)
                partners._increase_rank('customer_rank')

        MoveLine = self.env['account.move.line'].with_context(check_move_validity=False)
        _logger.info('End _accumulate_amounts')
        data.update({
            'taxes':                               taxes,
            'sales':                               sales,
            'stock_expense':                       stock_expense,
            'split_receivables':                   split_receivables,
            'combine_receivables':                 combine_receivables,
            'split_receivables_cash':              split_receivables_cash,
            'combine_receivables_cash':            combine_receivables_cash,
            'invoice_receivables':                 invoice_receivables,
            'stock_output':                        stock_output,
            'order_account_move_receivable_lines': order_account_move_receivable_lines,
            'MoveLine':                            MoveLine
        })
        return data

    # def _create_non_reconciliable_move_lines(self, data):
    #     # Create account.move.line records for
    #     #   - sales
    #     #   - taxes
    #     #   - stock expense
    #     #   - non-cash split receivables (not for automatic reconciliation)
    #     #   - non-cash combine receivables (not for automatic reconciliation)
    #     taxes = data.get('taxes')
    #     sales = data.get('sales')
    #     stock_expense = data.get('stock_expense')
    #     split_receivables = data.get('split_receivables')
    #     combine_receivables = data.get('combine_receivables')
    #     MoveLine = data.get('MoveLine')

    #     tax_vals = [self._get_tax_vals(key, amounts['amount'], amounts['amount_converted'], amounts['base_amount_converted']) for key, amounts in taxes.items() if amounts['amount']]
    #     # Check if all taxes lines have account_id assigned. If not, there are repartition lines of the tax that have no account_id.
    #     tax_names_no_account = [line['name'] for line in tax_vals if line['account_id'] == False]
    #     if len(tax_names_no_account) > 0:
    #         error_message = _(
    #             'Unable to close and validate the session.\n'
    #             'Please set corresponding tax account in each repartition line of the following taxes: \n%s'
    #         ) % ', '.join(tax_names_no_account)
    #         raise UserError(error_message)

    #     MoveLine.create(
    #         tax_vals
    #         + [self._get_sale_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in sales.items()]
    #         + [self._get_stock_expense_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in stock_expense.items()]
    #         + [self._get_split_receivable_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in split_receivables.items()]
    #         + [self._get_combine_receivable_vals(key, amounts['amount'], amounts['amount_converted']) for key, amounts in combine_receivables.items()]
    #     )
    #     return data

    # def _create_cash_statement_lines_and_cash_move_lines(self, data):
    #     # Create the split and combine cash statement lines and account move lines.
    #     # Keep the reference by statement for reconciliation.
    #     # `split_cash_statement_lines` maps `statement` -> split cash statement lines
    #     # `combine_cash_statement_lines` maps `statement` -> combine cash statement lines
    #     # `split_cash_receivable_lines` maps `statement` -> split cash receivable lines
    #     # `combine_cash_receivable_lines` maps `statement` -> combine cash receivable lines
    #     MoveLine = data.get('MoveLine')
    #     split_receivables_cash = data.get('split_receivables_cash')
    #     combine_receivables_cash = data.get('combine_receivables_cash')

    #     statements_by_journal_id = {statement.journal_id.id: statement for statement in self.statement_ids}
    #     # handle split cash payments
    #     split_cash_statement_line_vals = defaultdict(list)
    #     split_cash_receivable_vals = defaultdict(list)
    #     for payment, amounts in split_receivables_cash.items():
    #         statement = statements_by_journal_id[payment.payment_method_id.cash_journal_id.id]
    #         split_cash_statement_line_vals[statement].append(self._get_statement_line_vals(statement, payment.payment_method_id.receivable_account_id, amounts['amount'], date=payment.payment_date, partner=payment.pos_order_id.partner_id))
    #         split_cash_receivable_vals[statement].append(self._get_split_receivable_vals(payment, amounts['amount'], amounts['amount_converted']))
    #     # handle combine cash payments
    #     combine_cash_statement_line_vals = defaultdict(list)
    #     combine_cash_receivable_vals = defaultdict(list)
    #     for payment_method, amounts in combine_receivables_cash.items():
    #         if not float_is_zero(amounts['amount'] , precision_rounding=self.currency_id.rounding):
    #             statement = statements_by_journal_id[payment_method.cash_journal_id.id]
    #             combine_cash_statement_line_vals[statement].append(self._get_statement_line_vals(statement, payment_method.receivable_account_id, amounts['amount']))
    #             combine_cash_receivable_vals[statement].append(self._get_combine_receivable_vals(payment_method, amounts['amount'], amounts['amount_converted']))
    #     # create the statement lines and account move lines
    #     BankStatementLine = self.env['account.bank.statement.line']
    #     split_cash_statement_lines = {}
    #     combine_cash_statement_lines = {}
    #     split_cash_receivable_lines = {}
    #     combine_cash_receivable_lines = {}
    #     for statement in self.statement_ids:
    #         split_cash_statement_lines[statement] = BankStatementLine.create(split_cash_statement_line_vals[statement])
    #         combine_cash_statement_lines[statement] = BankStatementLine.create(combine_cash_statement_line_vals[statement])
    #         split_cash_receivable_lines[statement] = MoveLine.create(split_cash_receivable_vals[statement])
    #         combine_cash_receivable_lines[statement] = MoveLine.create(combine_cash_receivable_vals[statement])

    #     data.update(
    #         {'split_cash_statement_lines':    split_cash_statement_lines,
    #          'combine_cash_statement_lines':  combine_cash_statement_lines,
    #          'split_cash_receivable_lines':   split_cash_receivable_lines,
    #          'combine_cash_receivable_lines': combine_cash_receivable_lines
    #          })
    #     return data

    # def _create_invoice_receivable_lines(self, data):
    #     # Create invoice receivable lines for this session's move_id.
    #     # Keep reference of the invoice receivable lines because
    #     # they are reconciled with the lines in order_account_move_receivable_lines
    #     MoveLine = data.get('MoveLine')
    #     invoice_receivables = data.get('invoice_receivables')

    #     invoice_receivable_vals = defaultdict(list)
    #     invoice_receivable_lines = {}
    #     for partner, amounts in invoice_receivables.items():
    #         commercial_partner = partner.commercial_partner_id
    #         account_id = commercial_partner.property_account_receivable_id.id
    #         invoice_receivable_vals[commercial_partner].append(self._get_invoice_receivable_vals(account_id, amounts['amount'], amounts['amount_converted'], partner=commercial_partner))
    #     for commercial_partner, vals in invoice_receivable_vals.items():
    #         account_id = commercial_partner.property_account_receivable_id.id
    #         receivable_lines = MoveLine.create(vals)
    #         for receivable_line in receivable_lines:
    #             if (not receivable_line.reconciled):
    #                 if account_id not in invoice_receivable_lines:
    #                     invoice_receivable_lines[account_id] = receivable_line
    #                 else:
    #                     invoice_receivable_lines[account_id] |= receivable_line

    #     data.update({'invoice_receivable_lines': invoice_receivable_lines})
    #     return data

    # def _create_stock_output_lines(self, data):
    #     # Keep reference to the stock output lines because
    #     # they are reconciled with output lines in the stock.move's account.move.line
    #     MoveLine = data.get('MoveLine')
    #     stock_output = data.get('stock_output')

    #     stock_output_vals = defaultdict(list)
    #     stock_output_lines = {}
    #     for output_account, amounts in stock_output.items():
    #         stock_output_vals[output_account].append(self._get_stock_output_vals(output_account, amounts['amount'], amounts['amount_converted']))
    #     for output_account, vals in stock_output_vals.items():
    #         stock_output_lines[output_account] = MoveLine.create(vals)

    #     data.update({'stock_output_lines': stock_output_lines})
    #     return data

    # def _create_balancing_line(self, data):
    #     imbalance_amount = 0
    #     for line in self.move_id.line_ids:
    #         # it is an excess debit so it should be credited
    #         imbalance_amount += line.debit - line.credit

    #     if (not float_is_zero(imbalance_amount, precision_rounding=self.currency_id.rounding)):
    #         balancing_vals = self._prepare_balancing_line_vals(imbalance_amount, self.move_id)
    #         MoveLine = data.get('MoveLine')
    #         MoveLine.create(balancing_vals)

    #     return data
    
    # def _create_extra_move_lines(self, data):
    #     # Keep reference to the stock output lines because
    #     # they are reconciled with output lines in the stock.move's account.move.line
    #     MoveLine = data.get('MoveLine')

    #     MoveLine.create(self._get_extra_move_lines_vals())
    #     return data

    # def _reconcile_account_move_lines(self, data):
    #     # reconcile cash receivable lines
    #     split_cash_statement_lines = data.get('split_cash_statement_lines')
    #     combine_cash_statement_lines = data.get('combine_cash_statement_lines')
    #     split_cash_receivable_lines = data.get('split_cash_receivable_lines')
    #     combine_cash_receivable_lines = data.get('combine_cash_receivable_lines')
    #     order_account_move_receivable_lines = data.get('order_account_move_receivable_lines')
    #     invoice_receivable_lines = data.get('invoice_receivable_lines')
    #     stock_output_lines = data.get('stock_output_lines')

    #     for statement in self.statement_ids:
    #         if not self.config_id.cash_control:
    #             statement.write({'balance_end_real': statement.balance_end})
    #         statement.button_confirm_bank()
    #         all_lines = (
    #               split_cash_statement_lines[statement].mapped('journal_entry_ids').filtered(lambda aml: aml.account_id.internal_type == 'receivable')
    #             | combine_cash_statement_lines[statement].mapped('journal_entry_ids').filtered(lambda aml: aml.account_id.internal_type == 'receivable')
    #             | split_cash_receivable_lines[statement]
    #             | combine_cash_receivable_lines[statement]
    #         )
    #         accounts = all_lines.mapped('account_id')
    #         lines_by_account = [all_lines.filtered(lambda l: l.account_id == account) for account in accounts]
    #         for lines in lines_by_account:
    #             lines.reconcile()

    #     # reconcile invoice receivable lines
    #     for account_id in order_account_move_receivable_lines:
    #         ( order_account_move_receivable_lines[account_id]
    #         | invoice_receivable_lines.get(account_id, self.env['account.move.line'])
    #         ).reconcile()

    #     # reconcile stock output lines
    #     orders_to_invoice = self.order_ids.filtered(lambda order: not order.is_invoiced)
    #     stock_moves = (
    #         orders_to_invoice.mapped('picking_id') +
    #         self.env['stock.picking'].search([('origin', 'in', orders_to_invoice.mapped(lambda o: '%s - %s' % (self.name, o.name)))])
    #     ).mapped('move_lines')
    #     stock_account_move_lines = self.env['account.move'].search([('stock_move_id', 'in', stock_moves.ids)]).mapped('line_ids')
    #     for account_id in stock_output_lines:
    #         ( stock_output_lines[account_id]
    #         | stock_account_move_lines.filtered(lambda aml: aml.account_id == account_id)
    #         ).filtered(lambda aml: not aml.reconciled).reconcile()
    #     return data

    #     _logger.info('Start _reconcile_account_move_lines')
    #     super(PosSession, self)._reconcile_account_move_lines(data)
    #     _logger.info('Start _reconcile_account_move_lines')
                    
    def _create_account_move(self):
        return super(PosSession, self.with_context({
            'department_id': self.config_id.department_id.id,
            'branch_id': self.config_id.branch_id.id,
        }))._create_account_move()
