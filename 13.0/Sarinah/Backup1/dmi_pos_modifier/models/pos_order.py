from odoo import fields, models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


import logging
_logger = logging.getLogger(__name__)



class InheritPosOrder(models.Model):
    _inherit = 'pos.order'

    is_wrong_promotion = fields.Boolean(string="Wrong Promotion", default=False)
    refferal_name = fields.Char(string="Refferal Name")
    refferal_name2 = fields.Char(string="Refferal Name")

    @api.model
    def get_date_server(self):
        """Returns the current server date and time with 7 hours added."""
        server_time = fields.Datetime.now()
        adjusted_time = server_time + timedelta(hours=7)
        return adjusted_time

    @api.model
    def _order_fields(self, ui_order):
        fields_ori = super(InheritPosOrder, self)._order_fields(ui_order)
        if fields_ori.get('lines'):
            for line in fields_ori['lines']:
                if line[2]['discount'] > 0 and line[2]['custom_promotion_id'] in (None, False) and fields_ori['is_exchange_order']:
                    old_order = self.env['pos.order'].sudo().search([('pos_reference', '=', fields_ori['old_pos_reference'])], limit=1)
                    lines = old_order.lines.filtered(lambda l: l.product_id.id == line[2]['product_id'])
                    if lines :
                        line[2]['custom_promotion_id'] = lines[0].custom_promotion_id.id
                        line[2]['sarinah_shared'] = lines[0].sarinah_shared
                        line[2]['vendor_shared'] = lines[0].vendor_shared



        fields_ori['date_order'] = fields.Datetime.now()
        return fields_ori

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(InheritPosOrder, self).create_from_ui(orders, draft)
        for order in self.sudo().browse([o['id'] for o in order_ids]):
            if order.pos_ref_code_id:
                order.refferal_name = order.pos_ref_code_id.name
            if order.pos_ref_code2_id:
                order.refferal_name2 = order.pos_ref_code2_id.name

        return order_ids
    
    @api.model
    def search_return_order_length(self, config_data):
        today_date = datetime.today().strftime('%Y-%m-%d')
        if config_data['sh_load_order_by']:

            if config_data['sh_load_order_by'] == 'session_wise':

                if config_data['sh_session_wise_option'] == 'current_session':
                    order_data = self.env['pos.order'].search_read(
                        [('user_id', '=', self.env.user.id), ('session_id', '=', config_data['current_session_id'][0]),
                         ('state', '!=', 'cancel'),('date_order', '>=', (today_date + " 00:00:00")),
                         ('date_order', '<=', (today_date + " 24:00:00"))])

                if config_data['sh_session_wise_option'] == 'last_no_session':
                    all_session = self.env['pos.session'].search_read([])
                    for index, obj in enumerate(all_session):
                        if (index + 1) != len(all_session):
                            if (all_session[index]['stop_at'] and all_session[index + 1]):
                                if (all_session[index]['stop_at'] < all_session[index + 1]['stop_at']):
                                    temp = all_session[index];
                                    all_session[index] = all_session[index + 1];
                                    all_session[index + 1] = temp;
                    session = []
                    for x in range(0, config_data['sh_last_no_session']):
                        if x < len(all_session):
                            session.append(all_session[x]['id']);
                    if session:
                        order_data = self.env['pos.order'].search_read(
                            [('user_id', '=', self.env.user.id), ('session_id', 'in', session),
                             ('state', '!=', 'cancel'),('date_order', '>=', (today_date + " 00:00:00")),
                         ('date_order', '<=', (today_date + " 24:00:00"))])

            if config_data['sh_load_order_by'] == 'all':
                order_data = self.env['pos.order'].search_read(
                    [('user_id', '=', self.env.user.id), ('state', '!=', 'cancel'),('date_order', '>=', (today_date + " 00:00:00")),
                         ('date_order', '<=', (today_date + " 24:00:00"))])

            if config_data['sh_load_order_by'] == 'day_wise':

                if config_data['sh_day_wise_option'] == 'current_day':

                    order_data = self.env['pos.order'].search_read(
                        [('user_id', '=', self.env.user.id), ('date_order', '>=', (today_date + " 00:00:00")),
                         ('date_order', '<=', (today_date + " 24:00:00")), ('state', '!=', 'cancel')])

                if config_data['sh_day_wise_option'] == 'last_no_day':
                    if config_data['sh_last_no_days']:
                        today_date = datetime.today().strftime('%Y-%m-%d')
                        last_date = datetime.today() - timedelta(days=config_data['sh_last_no_days'])
                        last_date = last_date.strftime('%Y-%m-%d')
                        order_data = self.env['pos.order'].search_read(
                            [('user_id', '=', self.env.user.id), ('date_order', '<=', (today_date + " 24:00:00")),
                             ('date_order', '>', (last_date + " 24:00:00")), ('state', '!=', 'cancel')])
        order_line = []
        if order_data and len(order_data) > 0:
            order_ids = []
            for each_order in order_data:
                order_ids.append(each_order.get('id'))
            order_line = self.env['pos.order.line'].search_read([('order_id', 'in', order_ids)])

        # # Luk untuk reprint receipt
        # return {'order':order_data,'order_line':order_line}

        payment_line = []
        if order_data and len(order_data) > 0:
            order_ids = []
            for each_order in order_data:
                order_ids.append(each_order.get('id'))
            payment_line = self.env['pos.payment'].search_read(
                [('pos_order_id', 'in', order_ids)])
        return {'order': order_data, 'order_line': order_line, 'payment_line': payment_line}

    # @api.model
    # def search_return_order(self, config_data, page_number, name=False, date=False):
    #     debug = {}
    #     today_date = datetime.today().strftime('%Y-%m-%d')

    #     limit = 10  # int(config_data['sh_how_many_order_per_page'])

    #     showFrom = limit * (int(page_number) - 1)
    #     showTo = showFrom + limit

    #     debug['showFrom'] = showFrom
    #     debug['showTo'] = showTo
    #     debug['name'] = name
    #     debug['date'] = date

    #     # domain = [('config_id.branch_id','=',config_data['branch_id'][0]),('state','!=','cancel'),('is_return_order','=',False),('is_exchange_order','=',False)]
    #     # Yayat, Show all order. normal, return or exchange
    #     domain = [('config_id.branch_id', '=', config_data['branch_id'][0]), ('state', '!=', 'cancel')]

    #     if name:
    #         domain.append(('pos_reference', 'ilike', name))

    #     last_date = datetime.today() - timedelta(days=(config_data['sh_last_no_days'] or 7))
    #     last_date = last_date.strftime('%Y-%m-%d')

    #     if date:
    #         datetime_from = datetime.strptime(('%s' % date), '%Y-%m-%d')
    #         datetime_to = datetime.strptime(('%s' % date), '%Y-%m-%d') + relativedelta(days=0, hours=23, minute=59,
    #                                                                                    second=59)

    #         domain.append(('date_order', '>=', datetime_from))
    #         domain.append(('date_order', '<=', datetime_to))
    #     else:
    #         domain.append(('date_order', '>=', (today_date + " 00:00:00")))
    #         domain.append(('date_order', '<=', (today_date + " 24:00:00")))
    #     order_data = self.env['pos.order'].search_read(domain, limit=limit, offset=showFrom)
    #     total = self.env['pos.order'].search_count(domain) / limit

    #     order_line = []
    #     if order_data and len(order_data) > 0:
    #         order_ids = []
    #         for each_order in order_data:
    #             order_ids.append(each_order.get('id'))
    #         order_line = self.env['pos.order.line'].search_read([('order_id', 'in', order_ids)])

    #     payment_line = []
    #     if order_data and len(order_data) > 0:
    #         order_ids = []
    #         for each_order in order_data:
    #             order_ids.append(each_order.get('id'))
    #         payment_line = self.env['pos.payment'].search_read(
    #             [('pos_order_id', 'in', order_ids)])
    #     return {'order': order_data, 'order_line': order_line, 'payment_line': payment_line, 'debug': debug,
    #             'total': total}

    @api.model
    def search_return_order(self, config_data, page_number, name=False, date=False):    
        debug = {}
        limit = 10 # int(config_data['sh_how_many_order_per_page'])

        showFrom = limit * (int(page_number) - 1)
        showTo = showFrom + limit

        debug['showFrom'] = showFrom
        debug['showTo'] = showTo
        debug['name'] = name
        debug['date'] = date
        
        domain = []
        
        if name:
            domain.append(('pos_reference', 'like', name))

        last_date = datetime.today() - timedelta(days = (config_data['sh_last_no_days'] or 7) )
        last_date = last_date.strftime('%Y-%m-%d')

        if date:
            datetime_from = datetime.strptime(('%s' % date), '%Y-%m-%d')
            datetime_to = datetime.strptime(('%s' % date), '%Y-%m-%d') + relativedelta(days=0, hours=23, minute=59, second=59)

            domain.append(('date_order', '>=', datetime_from))
            domain.append(('date_order', '<=', datetime_to))
        # else:
        #     domain.append(('date_order', '>=', last_date))

        _logger.info('Search Order')
        _logger.info(datetime.now())
        # order_data = self.env['pos.order'].search_read(domain,limit=limit, offset=showFrom)
        # total = self.env['pos.order'].search_count(domain) / limit
        _logger.info(domain)
        order_data = self.env['pos.order'].search_read(domain)
        if not order_data:
            return {'order': [], 'order_line': [], 'payment_line': [],'debug':debug,'total':0, 'product': []}

        total = len(order_data)
        pricelist_id = order_data[0]['pricelist_id'][0]
                       
        _logger.info('Search Orderline')
        _logger.info(datetime.now())
        order_line = []
        product_list = []
        if order_data and len(order_data) > 0:
            order_ids = []
            for each_order in order_data:
                order_ids.append(each_order.get('id'))
            order_line = self.env['pos.order.line'].search_read([('order_id','in',order_ids)])
            _logger.info(order_line)
            for line in order_line:                
                product_id = self.env['product.product'].prepare_product_product(line['product_id'][0], pricelist_id)
                product_list.append(product_id)
                            
        # # Luk untuk reprint receipt
        # return {'order':order_data,'order_line':order_line}

        _logger.info('Search Payment')
        _logger.info(datetime.now())
        payment_line = []
        if order_data and len(order_data) > 0:
            order_ids = []
            for each_order in order_data:
                order_ids.append(each_order.get('id'))
            payment_line = self.env['pos.payment'].search_read(
                [('pos_order_id', 'in', order_ids)])
        return {'order': order_data, 'order_line': order_line, 'payment_line': payment_line,'debug':debug,'total':total, 'product': product_list}

    def create(self, vals):
        order = super(InheritPosOrder, self).create(vals)
        order.check_promotion()
        return order

    @api.model
    def check_promotion(self):
        for rec in self:
            # Mendapatkan produk voucher yang bertipe 'service'
            voucher_product_ids = rec.lines.mapped('product_id').filtered(lambda p: p.type == 'service').ids
            if not voucher_product_ids:
                continue
            for line in rec.lines.filtered(lambda l: l.product_id.type == 'product'):
                if line.custom_promotion_id and line.custom_promotion_id.promotion_type == 'buy_x_get_dis_y':
                    # Mengecek apakah produk voucher dalam promosi tidak ada di dalam list voucher_product_ids
                    if line.custom_promotion_id.parent_product_ids :
                        for voucher_product in line.custom_promotion_id.parent_product_ids:
                            if voucher_product.id not in voucher_product_ids:
                                rec.sudo().is_wrong_promotion = True
                                promo = rec.get_promotion(line.product_id.id, voucher_product_ids, rec)
                                # print('promo',promo)
                                if promo:
                                    line.sudo().custom_fix_promotion_id = promo.id
                                    line.fix_shared_promotion()
                    else :
                        rec.sudo().is_wrong_promotion = True
                        promo = rec.get_promotion(line.product_id.id, voucher_product_ids, rec)
                        # print('promo', promo)
                        if promo:
                            line.sudo().custom_fix_promotion_id = promo.id
                            line.fix_shared_promotion()

    def get_promotion(self, product_id, voucher_product_ids, rec):
        promotion = self.env['pos.promotion'].sudo().search([
            ('promotion_type', '=', 'buy_x_get_dis_y'),
            ('parent_product_ids', 'in', voucher_product_ids),
            ('from_date', '<=', rec.date_order),
            ('to_date', '>=', rec.date_order),
            ('available_in_pos', 'in', (rec.session_id.config_id.id, False))
        ])

        for promo in promotion:
            # Memeriksa apakah produk yang diberikan termasuk dalam promo
            if product_id in promo.pos_quntity_dis_ids.mapped('product_id_dis').ids:
                return promo

    def fix_shared_promotion(self):
        for rec in self:
            rec.lines.fix_shared_promotion()

    def unfix_shared_promotion(self):
        for rec in self:
            rec.lines.unfix_shared_promotion()


class inherit_Pos_Order_line(models.Model):
    _inherit = 'pos.order.line'

    custom_fix_promotion_id = fields.Many2one(comodel_name='pos.promotion', string="Fix Promotion")

    def fix_shared_promotion(self):
        for line in self :
            if line.custom_fix_promotion_id:
                line.sudo().write({'sarinah_shared': line.custom_fix_promotion_id.sarinah_shared,'vendor_shared': line.custom_fix_promotion_id.vendor_shared})

    def unfix_shared_promotion(self):
        for line in self :
            if line.custom_promotion_id:
                line.sudo().write({'sarinah_shared': line.custom_promotion_id.sarinah_shared,'vendor_shared': line.custom_promotion_id.vendor_shared})


    # def write(self, vals):
    #     res = super(inherit_Pos_Order_line, self).write(vals)
    #     return res

class PosPayment(models.Model):
    _inherit = 'pos.payment'

    @api.model
    def create(self,vals):
        if vals.get('payment_date'):
            vals['payment_date'] = fields.Datetime.now()
        res = super(PosPayment, self).create(vals)
        return res