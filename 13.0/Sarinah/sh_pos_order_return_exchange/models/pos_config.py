# Copyright (C) Softhealer Technologies.
from odoo import fields, models, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)



class PosConfig(models.Model):
    _inherit = 'pos.config'

    sh_allow_return = fields.Boolean(string="Allow Return Order")
    sh_return_more_qty = fields.Boolean(
        string="Allow Return More Than Purchase Item")
    sh_return_print_receipt = fields.Boolean(
        string="Print Information In Receipt")
    sh_allow_exchange = fields.Boolean(string="Allow Exchange Order")
    sh_exchange_print_receipt = fields.Boolean(
        string="Print Information In Receipt")


class ProductProduct(models.Model):
    _inherit = "product.product"

    def prepare_product_product(self, product_id, pricelist_id): 
        product = {}
        product_id = self.env['product.product'].browse(product_id)
        if not product_id:
            return False
        
        domain = [
            ('pricelist_id','=', pricelist_id),
            ('product_id','=', product_id.id)
        ]
        
        product.update(
            {
                "id": product_id.id,
                "display_name": product_id.name,
                "lst_price": product_id.lst_price,
                "standard_price": product_id.standard_price,
                "categ_id": [
                    product_id.categ_id.id,
                    product_id.categ_id.name
                ],
                "pos_categ_id": False,
                "taxes_id": product_id.taxes_id.ids,                  
                "barcode": product_id.barcode,
                "default_code": product_id.default_code,
                "to_weight": product_id.to_weight,
                "uom_id": [
                    product_id.uom_id.id,
                    product_id.uom_id.name
                ],
                "description_sale": product_id.description_sale,
                "description": product_id.description,
                "product_tmpl_id": [
                    product_id.product_tmpl_id.id,
                    product_id.product_tmpl_id.name
                ],
                "tracking": "none",
                "qty_available": product_id.qty_available,
                "sh_product_non_returnable": product_id.sh_product_non_returnable,
                "sh_product_non_exchangeable": product_id.sh_product_non_exchangeable
                
            }
        )    
        pricelist_items = self.env['product.pricelist.item'].search(domain)
        available_pricelist_items = []
        for pricelist_item in pricelist_items:
            var = {
                "id": pricelist_item.id,
                "product_tmpl_id": [
                    pricelist_item.product_id.product_tmpl_id.id,
                    pricelist_item.product_id.product_tmpl_id.name
                ],
                "product_id": [
                    pricelist_item.product_id.id,
                    pricelist_item.product_id.name
                ],
                "categ_id": False,
                "min_quantity": pricelist_item.min_quantity,
                "base": pricelist_item.base,
                "pricelist_id": [
                    pricelist_item.pricelist_id.id,
                    pricelist_item.pricelist_id.name
                ],
                "price_surcharge": pricelist_item.price_surcharge,
                "price_discount": pricelist_item.price_discount,
                "price_round": pricelist_item.price_round,
                "price_min_margin": pricelist_item.price_min_margin,
                "price_max_margin": pricelist_item.price_max_margin,          
                "company_id": [
                    pricelist_item.company_id.id,
                    pricelist_item.company_id.name,
                ],
                "currency_id": [
                    pricelist_item.currency_id.id,
                    pricelist_item.currency_id.name,
                ],
                "active": pricelist_item.active,
                "date_start": pricelist_item.date_start and pricelist_item.date_start.strftime('%Y-%m-%d %H:%M:%S') or False,
                "date_end": pricelist_item.date_end and pricelist_item.date_end.strftime('%Y-%m-%d %H:%M:%S') or False,
                "compute_price": pricelist_item.compute_price,
                "fixed_price": pricelist_item.fixed_price,
                "percent_price": pricelist_item.percent_price,
                "name": pricelist_item.name,
                "price": pricelist_item.price,
                "offer_msg": pricelist_item.offer_msg,
                "is_display_timer": pricelist_item.is_display_timer,
                "branch_id": [
                    pricelist_item.branch_id.id,
                    pricelist_item.branch_id.name
                ],
                "department_id": [
                    pricelist_item.department_id.id,
                    pricelist_item.department_id.name,
                ],
                # "vendor_product_id": [
                #     pricelist_item.vendor_product_id.id,
                #     pricelist_item.vendor_product_id.name,
                # ],
                "display_name": pricelist_item.display_name,
            }
            _logger.info(var)
            available_pricelist_items.append(var)
            
        product.update({
            'available_pricelist_items': available_pricelist_items
        })
        return product
        
    sh_product_non_returnable = fields.Boolean(string="Non Returnable")
    sh_product_non_exchangeable = fields.Boolean(string="Non Exchangeable")

    @api.model
    def search_no_change(self):
        product = self.env['product.product'].search_read([('name', '=', 'No Change')], limit=1)
        return product[0] if len(product) > 0 else False


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    sh_return_qty = fields.Float(string="Return Qty.")
    sh_exchange_qty = fields.Float(string="Exchange Qty.")


class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    @api.depends('date_order')    
    def get_allow_to_exchange(self):
        for row in self:
            if row.date_order >= datetime.now() + timedelta(days=-7) :
                row.is_allow_to_exchange = True
            else:
                row.is_allow_to_exchange = False
    
    is_allow_to_exchange = fields.Boolean('Still Allow to Exchange', compute="get_allow_to_exchange")

    is_return_order = fields.Boolean(string="Is Return Order?")
    is_exchange_order = fields.Boolean(string="Is Exchange Order?")
    old_pos_reference = fields.Char(string="Return Order")
    return_status = fields.Selection([
        ('nothing_return', 'Nothing Returned'),
        ('partialy_return', 'Partialy Returned'),
        ('fully_return', 'Fully Returned')
    ], string="Return Status", default='nothing_return',
        readonly=True, copy=False, help="Return status of Order")
    total_return_order = fields.Integer(
        compute='_return_order_total', string="Total Return Order",)
    total_exchange_order = fields.Integer(
        compute='_exchange_order_total', string="Total Exchange Order",)    
    
    
    @api.model
    def get_order_paymentlines(self, order_name):
        paymentlines = self.env['pos.payment'].search([('pos_order_id.pos_reference', '=', order_name)])
        data = []
        for p in paymentlines:
            data.append({
                'name': p.payment_method_id.name,
                'amount': p.amount
            })

        res = []
        for d in data:
            if d['name'] not in res:
                res.append(d['name'])

        res_2 = []
        for r in res:
            amount = 0
            for d in data:
                if d['name'] == r:
                    amount += d['amount']

            res_2.append({
                'name': r,
                'amount': amount
            })

        return res_2

    @api.model
    def search_return_exchange_order(self,config_data,page_number):
        showFrom = int(config_data['sh_how_many_order_per_page']) * (int(page_number) - 1)
        showTo = showFrom + int(config_data['sh_how_many_order_per_page'])
        
        if config_data['sh_load_order_by']:
            
            if config_data['sh_load_order_by'] == 'session_wise':
                
                if config_data['sh_session_wise_option'] == 'current_session':
                    order_data = self.env['pos.order'].search_read(['|',('user_id','=',self.env.user.id),('assigned_config','=',config_data['id']),('session_id','=',config_data['current_session_id'][0]),('state','!=','cancel'),'|',('is_return_order','=',True),('is_exchange_order','=',True)],limit=showTo)
                
                if config_data['sh_session_wise_option'] == 'last_no_session':
                    all_session = self.env['pos.session'].search_read([])
                    for index, obj in enumerate(all_session):
                        if (index+1) != len(all_session):
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
                        order_data = self.env['pos.order'].search_read(['|',('user_id','=',self.env.user.id),('assigned_config','=',config_data['id']),('session_id','in',session),('state','!=','cancel'),'|',('is_return_order','=',True),('is_exchange_order','=',True)],limit=showTo)
            
            if config_data['sh_load_order_by'] == 'all':   
                order_data = self.env['pos.order'].search_read(['|',('user_id','=',self.env.user.id),('assigned_config','=',config_data['id']),('state','!=','cancel'),'|',('is_return_order','=',True),('is_exchange_order','=',True)],limit=showTo)
            
            if config_data['sh_load_order_by'] == 'day_wise':
                
                if config_data['sh_day_wise_option'] == 'current_day':
                    today_date = datetime.today().strftime('%Y-%m-%d')
                    order_data = self.env['pos.order'].search_read(['|',('user_id','=',self.env.user.id),('assigned_config','=',config_data['id']),('date_order','>=',(today_date + " 00:00:00")),('date_order','<=',(today_date + " 24:00:00")),('state','!=','cancel'),'|',('is_return_order','=',True),('is_exchange_order','=',True)],limit=showTo)
                
                if config_data['sh_day_wise_option'] == 'last_no_day':
                    if config_data['sh_last_no_days']:
                        today_date = datetime.today().strftime('%Y-%m-%d')
                        last_date = datetime.today() - timedelta(days = config_data['sh_last_no_days'] )
                        last_date = last_date.strftime('%Y-%m-%d')
                        order_data = self.env['pos.order'].search_read(['|',('user_id','=',self.env.user.id),('assigned_config','=',config_data['id']),('date_order','<=',(today_date + " 24:00:00")),('date_order','>',(last_date + " 24:00:00")),('state','!=','cancel'),'|',('is_return_order','=',True),('is_exchange_order','=',True)],limit=showTo)
        order_data = order_data[showFrom:showTo]
        order_line = []
        if order_data and len(order_data) > 0:
            order_ids = []
            for each_order in order_data:
                order_ids.append(each_order.get('id'))
            order_line = self.env['pos.order.line'].search_read([('order_id','in',order_ids)])
        return {'order':order_data,'order_line':order_line}
    
    @api.model
    def search_return_order_length(self, config_data):
        
        
        if config_data['sh_load_order_by']:
            
            if config_data['sh_load_order_by'] == 'session_wise':
                
                if config_data['sh_session_wise_option'] == 'current_session':
                    order_data = self.env['pos.order'].search_read([('user_id','=',self.env.user.id),('session_id','=',config_data['current_session_id'][0]),('state','!=','cancel')])
                
                if config_data['sh_session_wise_option'] == 'last_no_session':
                    all_session = self.env['pos.session'].search_read([])
                    for index, obj in enumerate(all_session):
                        if (index+1) != len(all_session):
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
                        order_data = self.env['pos.order'].search_read([('user_id','=',self.env.user.id),('session_id','in',session),('state','!=','cancel')])
            
            if config_data['sh_load_order_by'] == 'all':   
                order_data = self.env['pos.order'].search_read([('user_id','=',self.env.user.id),('state','!=','cancel')])
            
            if config_data['sh_load_order_by'] == 'day_wise':
                
                if config_data['sh_day_wise_option'] == 'current_day':
                    today_date = datetime.today().strftime('%Y-%m-%d')
                    order_data = self.env['pos.order'].search_read([('user_id','=',self.env.user.id),('date_order','>=',(today_date + " 00:00:00")),('date_order','<=',(today_date + " 24:00:00")),('state','!=','cancel')])
                
                if config_data['sh_day_wise_option'] == 'last_no_day':
                    if config_data['sh_last_no_days']:
                        today_date = datetime.today().strftime('%Y-%m-%d')
                        last_date = datetime.today() - timedelta(days = config_data['sh_last_no_days'] )
                        last_date = last_date.strftime('%Y-%m-%d')
                        order_data = self.env['pos.order'].search_read([('user_id','=',self.env.user.id),('date_order','<=',(today_date + " 24:00:00")),('date_order','>',(last_date + " 24:00:00")),('state','!=','cancel')])
        order_line = []
        if order_data and len(order_data) > 0:
            order_ids = []
            for each_order in order_data:
                order_ids.append(each_order.get('id'))
            order_line = self.env['pos.order.line'].search_read([('order_id','in',order_ids)])

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

    @api.model
    def search_return_order(self,config_data,page_number,name=False,date=False):
        debug = {}

        limit = 10 # int(config_data['sh_how_many_order_per_page'])

        showFrom = limit * (int(page_number) - 1)
        showTo = showFrom + limit

        debug['showFrom'] = showFrom
        debug['showTo'] = showTo
        debug['name'] = name
        debug['date'] = date

        domain = []
        #domain = [('config_id.branch_id','=',config_data['branch_id'][0]),('state','!=','cancel'),('is_return_order','=',False),('is_exchange_order','=',False)]
        #domain = [('config_id.branch_id','=',config_data['branch_id'][0]),('state','!=','cancel')]
        # domain = [('config_id.branch_id','=',config_data['branch_id'][0])]
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
        for order in order_data:
            if order['date_order'] > datetime.now() + timedelta(days=-7):
                order.is_allow_to_exchange = False
        total = len(order_data)
        pricelist_id = order_data[0]['pricelist_id'][0]
                
        # showFrom = int(config_data['sh_how_many_order_per_page']) * (int(page_number) - 1)
        # showTo = showFrom + int(config_data['sh_how_many_order_per_page'])

        # if config_data['sh_load_order_by']:

        #     if config_data['sh_load_order_by'] == 'session_wise':

        #         if config_data['sh_session_wise_option'] == 'current_session':
        #             order_data = self.env['pos.order'].search_read([('config_id.branch_id','=',config_data['branch_id'][0]),('session_id','=',config_data['current_session_id'][0]),('state','!=','cancel'),('is_return_order','=',False),('is_exchange_order','=',False)],limit=showTo)

        #         if config_data['sh_session_wise_option'] == 'last_no_session':
        #             all_session = self.env['pos.session'].search_read([])
        #             for index, obj in enumerate(all_session):
        #                 if (index+1) != len(all_session):
        #                     if (all_session[index]['stop_at'] and all_session[index + 1]):
        #                         if (all_session[index]['stop_at'] < all_session[index + 1]['stop_at']):
        #                             temp = all_session[index];
        #                             all_session[index] = all_session[index + 1];
        #                             all_session[index + 1] = temp;
        #             session = []
        #             for x in range(0, config_data['sh_last_no_session']):
        #                 if x < len(all_session):
        #                     session.append(all_session[x]['id']);
        #             if session:
        #                 order_data = self.env['pos.order'].search_read([('config_id.branch_id','=',config_data['branch_id'][0]),('session_id','in',session),('state','!=','cancel'),('is_return_order','=',False),('is_exchange_order','=',False)],limit=showTo)

        #     if config_data['sh_load_order_by'] == 'all':
        #         order_data = self.env['pos.order'].search_read([('config_id.branch_id','=',config_data['branch_id'][0]),('state','!=','cancel'),('is_return_order','=',False),('is_exchange_order','=',False)],limit=showTo)

        #     if config_data['sh_load_order_by'] == 'day_wise':

        #         if config_data['sh_day_wise_option'] == 'current_day':
        #             today_date = datetime.today().strftime('%Y-%m-%d')
        #             order_data = self.env['pos.order'].search_read([('config_id.branch_id','=',config_data['branch_id'][0]),('date_order','>=',(today_date + " 00:00:00")),('date_order','<=',(today_date + " 24:00:00")),('state','!=','cancel'),('is_return_order','=',False),('is_exchange_order','=',False)],limit=showTo)

        #         if config_data['sh_day_wise_option'] == 'last_no_day':
        #             if config_data['sh_last_no_days']:
        #                 today_date = datetime.today().strftime('%Y-%m-%d')
        #                 last_date = datetime.today() - timedelta(days = config_data['sh_last_no_days'] )
        #                 last_date = last_date.strftime('%Y-%m-%d')
        #                 order_data = self.env['pos.order'].search_read([('config_id.branch_id','=',config_data['branch_id'][0]),('date_order','<=',(today_date + " 24:00:00")),('date_order','>',(last_date + " 24:00:00")),('state','!=','cancel'),('is_return_order','=',False),('is_exchange_order','=',False)],limit=showTo)
        # order_data = order_data[showFrom:showTo]
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
                # product_id = self.env['product.product'].search-read([('id','=','line['product_id'][0]')])
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
    
    
    def _return_order_total(self):

        for each in self:
            return_order = self.search_read(
                [('old_pos_reference', '=', each.pos_reference), ('is_return_order', '=', True)])
            each.total_return_order = len(return_order)

    def _exchange_order_total(self):

        for each in self:
            exchange_order = self.search_read(
                [('old_pos_reference', '=', each.pos_reference), ('is_exchange_order', '=', True)])
            each.total_exchange_order = len(exchange_order)

    def action_view_return(self):
        return {
            'name': 'Return Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('old_pos_reference', '=', self.pos_reference), ('is_return_order', '=', True)],
            'res_model': 'pos.order',
            'target': 'current',
        }

    def action_view_exchange(self):
        return {
            'name': 'Exchange Order',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('old_pos_reference', '=', self.pos_reference), ('is_exchange_order', '=', True)],
            'res_model': 'pos.order',
            'target': 'current',
        }

    @api.model
    def _order_fields(self, ui_order):

        res = super(PosOrder, self)._order_fields(ui_order)
        res['is_return_order'] = ui_order.get(
            'is_return_order') if ui_order.get('is_return_order') else False
        res['is_exchange_order'] = ui_order.get(
            'is_exchange_order') if ui_order.get('is_exchange_order') else False
        res['old_pos_reference'] = ui_order.get(
            'old_pos_reference') if ui_order.get('old_pos_reference') else False
        if ui_order.get('is_return_order'):
            flag = True
            parent_order = self.search(
                [('pos_reference', '=', ui_order['old_pos_reference'])], limit=1)
            updated_lines = ui_order['lines']
            for uptd in updated_lines:
                if uptd[2].get('line_id'):
                    line = self.env['pos.order.line'].search([('order_id', '=', parent_order.id),
                                                              ('id', '=', uptd[2]['line_id'])], limit=1)
                    if not line:
                        line = self.env['pos.order.line'].search(
                            [('order_id', '=', parent_order.id), ('sh_line_id', '=', uptd[2]['old_line_id'])], limit=1)
                    if line:
                        line.sh_return_qty += -(uptd[2]['qty'])
            if parent_order.lines:
                for line in parent_order.lines:
                    if flag:
                        if line.qty > line.sh_return_qty:
                            flag = False
            if flag:
                parent_order.return_status = 'fully_return'
            else:
                parent_order.return_status = 'partialy_return'

        if ui_order.get('is_exchange_order'):
            flag = True
            parent_order = self.search(
                [('pos_reference', '=', ui_order['old_pos_reference'])], limit=1)
            updated_lines = ui_order['lines']
            for uptd in updated_lines:
                if uptd[2].get('line_id'):
                    line = self.env['pos.order.line'].search([('order_id', '=', parent_order.id),
                                                              ('id', '=', uptd[2]['line_id'])], limit=1)
                    if not line:
                        line = self.env['pos.order.line'].search(
                            [('order_id', '=', parent_order.id), ('sh_line_id', '=', uptd[2]['old_line_id'])], limit=1)
                    if line:
                        line.sh_return_qty += -(uptd[2]['qty'])
            if parent_order.lines:
                for line in parent_order.lines:
                    if flag:
                        if line.qty > line.sh_return_qty:
                            flag = False
            if flag:
                parent_order.return_status = 'fully_return'
            else:
                parent_order.return_status = 'partialy_return'

        return res

    @api.model
    def _process_order(self, order, draft, existing_order):
        order_id = super(PosOrder, self)._process_order(
            order, draft, existing_order)
        pos_order = self.search([('id', '=', order_id)], limit=1)
        old_pos_order = self.search(
            [('pos_reference', '=', pos_order.old_pos_reference)], limit=1)
        if old_pos_order:
            if pos_order.is_return_order:
                if old_pos_order.old_pos_reference:
                    old_pos_order.write(
                        {'old_pos_reference': old_pos_order.old_pos_reference + ' , ' + pos_order.pos_reference})
                else:
                    old_pos_order.write(
                        {'old_pos_reference': pos_order.pos_reference})
            if pos_order.is_exchange_order:
                if old_pos_order.old_pos_reference:
                    old_pos_order.write(
                        {'old_pos_reference': old_pos_order.old_pos_reference + ' , ' + pos_order.pos_reference})
                else:
                    old_pos_order.write(
                        {'old_pos_reference': pos_order.pos_reference})
        return order_id
