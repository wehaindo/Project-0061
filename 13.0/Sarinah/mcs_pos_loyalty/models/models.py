# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
import json
import logging
import pandas as pd

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def check_wallet_vernoss(self, partner, act='Check'):
        headers = {
            'content-type': "application/json",
            'Authorization': "Bearer %s" % self.env['ir.config_parameter'].sudo().get_param('vernoss_access_token'),
            'Api-Key': self.env['ir.config_parameter'].sudo().get_param('vernoss_api_key'),
        }

        _logger.info("\n########## check_wallet_vernoss: %s " % (partner))

        if 'id' in partner:
            if 'id' in partner:
                partner_id = partner['id']
            else:
                partner_id = partner.pop('id', False)
            loyalty_member = ""
            if partner_id:
                loyalty_member = self.env['res.partner'].browse(partner_id).loyalty_id

            url = "%s/loyalty-member/get-wallet?loyaltyMemberId=%s" % (
                self.env['ir.config_parameter'].sudo().get_param('vernoss_base_url'),
                loyalty_member
            )

            try:
                res = requests.get(url, headers=headers, verify=False)
                data = json.loads(res.content.decode('utf-8'))
                _logger.info("\n########## check_wallet_vernoss - Request to: %s " % (url))
                _logger.info("\n########## check_wallet_vernoss - Response: %s " % (data))
            except:
                return False

            if data:
                if 'responseCode' in data:
                    if data['responseCode'] == '00':
                        if 'payload' in data:
                            if data['payload']:
                                if data['payload']['totalAvailablePoints'] != 'NaN':
                                    self.browse(partner_id).write({
                                        'loyalty_points': data['payload']['totalAvailablePoints']
                                    })

                                if act == 'redeem':
                                    return data['payload']['totalAvailablePoints']
                    else:
                        return False
        else:
            partner_id = False

        return partner_id

    def check_wallet_vernoss_obj(self, act='Check'):
        headers = {
            'content-type': "application/json",
            'Authorization': "Bearer %s" % self.env['ir.config_parameter'].sudo().get_param('vernoss_access_token_ecommerce'),
            'Api-Key': self.env['ir.config_parameter'].sudo().get_param('vernoss_api_key_ecommerce'),
        }

        _logger.info("\n########## check_wallet_vernoss_obj - %s " % (self.name))

        partner_id = self.id

        loyalty_member = ""
        if partner_id:
            loyalty_member = self.env['res.partner'].browse(partner_id).loyalty_id

        url = "%s/loyalty-member/get-wallet?loyaltyMemberId=%s" % (
            self.env['ir.config_parameter'].sudo().get_param('vernoss_base_url_ecommerce'),
            loyalty_member
        )

        try:
            res = requests.get(url, headers=headers, verify=False)
            data = json.loads(res.content.decode('utf-8'))
            _logger.info("\n########## check_wallet_vernoss_obj - Request to: %s " % (url))
            _logger.info("\n########## check_wallet_vernoss_obj - Response: %s " % (data))
        except:
            return False

        if data:
            if 'responseCode' in data:
                if data['responseCode'] == '00':
                    if 'payload' in data:
                        if data['payload']:
                            if data['payload']['totalAvailablePoints'] != 'NaN':
                                self.browse(partner_id).write({
                                    'loyalty_points': data['payload']['totalAvailablePoints']
                                })

                            if act == 'redeem':
                                return data['payload']['totalAvailablePoints']
                else:
                    return False

        return False

    @api.model
    def create_from_ui(self, partner):
        """ create or modify a partner from the point of sale ui.
            partner contains the partner's fields. """
        # image is a dataurl, get the data after the comma
        if partner.get('image_1920'):
            partner['image_1920'] = partner['image_1920'].split(',')[1]

        if 'id' in partner:
            # partner_id = partner.pop('id', False)
            partner_id = partner['id']
            partner['customer_rank'] = 1
            if partner_id:  # Modifying existing partner
                if partner:
                    partner['is_loyalty'] = True

                _logger.info("\n########## res_partner - create_from_ui - partner: %s " % (partner))

                res_partner = self.browse(partner_id)
                if res_partner:
                    res_partner.write(partner)
            else:
                partner['lang'] = self.env.user.lang
                partner['is_loyalty'] = True

                _logger.info("\n########## res_partner - create_from_ui - partner: %s " % (partner))

                partner_id = self.create(partner).id
        else:
            partner['is_loyalty'] = True  # paksa
            partner['customer_rank'] = 1
            if 'is_loyalty' in partner and partner['is_loyalty'] == True:
                partner_id = self.create(partner).id

            _logger.info("\n########## res_partner - create_from_ui - partner: %s " % (partner))
            _logger.info("\n########## res_partner - create_from_ui - partner_id: %s " % (partner_id))

        return partner_id


class PosOrder(models.Model):
    _inherit = 'pos.order'

    loyalty_burn_points = fields.Float(help='The amount of Loyalty points the customer lost with this order')

    @api.model
    def sendEarnTransaction(self, order, payment):
        _logger.info("\n########## pos_order - sendEarnTransaction order: %s " % (order))

        _logger.info("\n########## pos_order - sendEarnTransaction payment: %s " % (payment))
        headers = {
            'content-type': "application/json",
            'Authorization': "Bearer %s" % self.env['ir.config_parameter'].sudo().get_param('vernoss_access_token'),
            'Api-Key': self.env['ir.config_parameter'].sudo().get_param('vernoss_api_key'),
        }

        partner_id = order.pop('partner_id', False)
        loyalty_member = ""
        if partner_id:
            loyalty_member = self.env['res.partner'].browse(partner_id).loyalty_id

        point = 0
        point_avg = 0
        total_line = 0
        amount_exclude = 0
        amount_discount = 0
        amount_discount_avg = 0
        for line in order['lines']:
            # print('########## LINE:\n', line)
            if 'reward_id' in line[2]:
                point = -1 * line[2]['price_subtotal_incl']

                if order['loyalty_burn_points'] == 0:
                    url = "%s/loyalty-member/burn-transaction" % (
                        self.env['ir.config_parameter'].sudo().get_param('vernoss_base_url')
                    )
                    code_burn = self.env['ir.config_parameter'].sudo().get_param('vernoss_product_code_burn')

                    pay = {
                        "loyaltyMemberId": loyalty_member,
                        "productCode": code_burn or "ZPTS",
                        "companyCode": "SARID",
                        "productPrice": 1,
                        "burnAmount": point,
                        "burnType": "EXACT",
                        "locationCode": "SARID_LOC",
                        "storeCode": "SARINAH_STORE",
                        "channelReference": "POS"
                    }

                    try:
                        # print('########## START BURN POINT:')
                        res = requests.post(url, json=pay, headers=headers, verify=False)
                        data = json.loads(res.content.decode('utf-8'))
                        # print('########## RESPONSE BURN POINT:\n',data)

                        _logger.info("\n########## sendEarnTransaction -  Request to: %s " % (url))
                        _logger.info("\n########## sendEarnTransaction -  Payload: %s " % (pay))
                        _logger.info("\n########## sendEarnTransaction -  Response: %s " % (data))
                    except:
                        return False

                    if data:
                        if 'responseCode' in data:
                            if data['responseCode'] != '00':
                                return {'responseMessage': data['responseMessage']}
            else:
                product = self.env['product.product'].search([('id', '=', line[2]['product_id'])])
                if line[2]['price_subtotal_incl'] >= 0 and product.type != 'service':
                    total_line += 1
                else:
                    if line[2]['price_subtotal_incl'] >= 0:
                        amount_exclude += line[2]['price_subtotal_incl']
                    else:
                        amount_discount += (-1 * line[2]['price_subtotal_incl'])

        # ganti karena migrasi vernos
        # url = "%s/loyalty-member/earn-transaction" % (self.env['ir.config_parameter'].sudo().get_param('vernoss_base_url'))
        url = "%s/loyalty-member/quick/earn-transaction" % (self.env['ir.config_parameter'].sudo().get_param('vernoss_base_url'))

        basketItems = []
        total_order = order['amount_total'] + point - amount_exclude + amount_discount

        for line in order['lines']:
            product = self.env['product.product'].search([('id', '=', line[2]['product_id'])])

            if 'reward_id' not in line[2]:
                product = self.env['product.product'].search([('id', '=', line[2]['product_id'])])
                if line[2]['price_subtotal_incl'] >= 0 and product.type != 'service':
                    if total_order != 0:
                        point_avg = line[2]['price_subtotal_incl'] / total_order * point
                        amount_discount_avg = line[2]['price_subtotal_incl'] / total_order * amount_discount
                    basketItems.append({
                        'productCode': product.default_code,
                        'retailValueBeforeTax': line[2]['price_subtotal_incl'] - point_avg - amount_discount_avg,
                    })

        paymentItems = []
        for line in payment:
            paymentMethod = self.env['pos.payment.method'].search([('id', '=', line['payment_method_id'])])
            method = "CASH"
            if paymentMethod.use_payment_terminal:
                if line['card_type']:
                    method = line['card_type']

            if paymentMethod.name == 'EDC':
                method = "DEBIT"

            if paymentMethod.for_gift_coupens:
                method = "VOUCHER"

            paymentItems.append({
                'paymentMethod': method,
                'paymentAmount': line['amount'],
            })

        if len(paymentItems) > 0:
            df = pd.DataFrame(paymentItems)
            g = df.groupby('paymentMethod', as_index=False).sum()
            paymentItems = g.to_dict('records')

        amount_total = order['amount_total'] - amount_exclude
        for x in paymentItems:
            if x['paymentMethod'] == 'CASH':
                x['paymentAmount'] -= order['amount_return']

            if amount_exclude > 0 and order['amount_total'] != 0:
                amount_exclude_avg = x['paymentAmount'] / order['amount_total'] * amount_exclude
                x['paymentAmount'] -= amount_exclude_avg

        payload = {
            "loyaltyMemberId": loyalty_member,
            "locationCode": "SARID_LOC",
            "storeCode": "SARINAH_STORE",
            "channelReference": "POS",
            "basketItems": basketItems,
            "totalPayment": amount_total,
            "paymentItems": paymentItems,
            'channelTransactionId': order.get('name')  # tambahan di vernoss versi baru, hanya ada di earn transaction. burn tidak ada.
        }

        try:
            res = requests.post(url, json=payload, headers=headers, verify=False)
            data = json.loads(res.content.decode('utf-8'))
            # print('######### RESPONSE VERNOS:\n', data)
            _logger.info("\n########## sendEarnTransaction -  Request to: %s " % (url))
            _logger.info("\n########## sendEarnTransaction -  Payload: %s " % (payload))
            _logger.info("\n########## sendEarnTransaction -  Response:%s " % (data))
        except:
            _logger.info("\n########## sendEarnTransactio - Error Vernoss ")
            return {'responseMessage': "Check Your Internet Connection!", 'burned_points': point}

        # print('######### CEK DATA RESPONSE:\n', data)

        if data:
            if 'responseCode' in data:
                if data['responseCode'] in ['00', '10']:
                    if 'payload' in data:
                        earn_points = 0
                        total_points = 0
                        if "memberWallet" in data['payload']:
                            if data['payload']['memberWallet']['totalAvailablePoints'] != 'NaN':
                                self.env['res.partner'].browse(partner_id).write({
                                    'loyalty_points': data['payload']['memberWallet']['totalAvailablePoints']
                                })
                                total_points = data['payload']['memberWallet']['totalAvailablePoints']

                        if "pointResult" in data['payload']:
                            for point in data['payload']["pointResult"]:
                                if 'earnedPoints' in point:
                                    if point["earnedPoints"] != 'NaN':
                                        earn_points += point["earnedPoints"]
                        return {
                            'point': total_points,
                            'earn_points': earn_points,
                            'burned_points': point,
                        }
                else:
                    return {'responseMessage': data['responseMessage'], 'burned_points': point}
        return {'responseMessage': "Check Your Internet Connection!", 'burned_points': point}

    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrder, self)._order_fields(ui_order)
        fields['loyalty_burn_points'] = ui_order.get('loyalty_burn_points', 0)
        return fields

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        for order in self.sudo().browse([o['id'] for o in order_ids]):
            if order.loyalty_points != 0 and order.partner_id:
                order.partner_id.loyalty_points -= order.loyalty_points
        return order_ids

    