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
from odoo import api, fields, models
from collections import OrderedDict
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager, \
    CustomerPortal


class VendorProductPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)        
        if 'product_count' in counters:
            domain = [
                ('product_owner','=', request.env.user.partner_id.id)
            ]
            count = request.env['product.template'].sudo().search_count(domain)
            values['product_count'] = count
        return values

    @http.route(['/my/products', '/my/products/page/<int:page>'], type='http', auth="public", website=True)    
    def portal_my_product(self, page=1, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()        
        domain = [
                ('product_owner','=', request.env.user.partner_id.id)
        ]
        product = request.env['product.template'].sudo().search(domain)
        searchbar_sortings = {
            'date': {'label': _('Newest'),
                     'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
        }
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'Active': {'label': _('Active'), 'domain': [('active', '=', True)]},
            'Archive': {'label': _('Archive'),'domain': [('active', '=', False)]},
        }
        if not filterby:
            filterby = 'all'
    
        domain += searchbar_filters[filterby]['domain']
        product_count = product.search_count(domain)
        pager = portal_pager(
            url="/my/products",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=product_count,
            page=page,
            step=self._items_per_page
        )
        products = product.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        values.update({
            'products': products,
            'page_name': 'products',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/products',
        })
        return request.render("weha_smart_pos_vendor_portal.portal_my_product",values)
            

    @http.route(['/my/product/<int:product_id>'], type='http', auth="user", website=True)
    def portal_my_vendor_product(self, product_id, access_token=None, **kw):
        """displaying the RFQ details"""
        product = request.env['product.template'].sudo().browse(int(product_id))
        product_product_id = request.env['product.product'].sudo().search([('product_tmpl_id','=',int(product_id))],limit=1)
        stock_quants = request.env['stock.quant'].sudo().search([('product_id','=',product_product_id.id)])
        values = {
            'product': product,
            'stock_quants': stock_quants
        }
        return request.render("weha_smart_pos_vendor_portal.portal_vendor_product_page", values)


class StockRequestPortal(CustomerPortal):
    
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'stock_request_count' in counters:
            count = request.env['stock.request'].sudo().search_count([])
            values['stock_request_count'] = count
        return values


    @http.route(['/my/stockrequests', '/my/stockrequests/page/<int:page>'], type='http', auth="public", website=True)    
    def portal_my_stock_request(self, page=1, sortby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()        
        stock_request = request.env['stock.request'].sudo().search([])
        searchbar_sortings = {
            'date': {'label': _('Newest'),
                     'order': 'create_date desc, id desc'},
            'name': {'label': _('Name'), 'order': 'name asc, id asc'},
        }
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'Active': {'label': _('Active'), 'domain': [('active', '=', True)]},
            'Archive': {'label': _('Archive'),'domain': [('active', '=', False)]},
        }
        if not filterby:
            filterby = 'all'

        domain = []
        domain += searchbar_filters[filterby]['domain']
        stock_request_count = stock_request.search_count(domain)
        pager = portal_pager(
            url="/my/stockrequests",
            url_args={'sortby': sortby, 'filterby': filterby},
            total=stock_request_count,
            page=page,
            step=self._items_per_page
        )
        stock_requests = stock_request.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        values.update({
            'stock_requests': stock_requests,
            'page_name': 'stock_requests',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'default_url': '/my/stockrequests',
        })
        return request.render("weha_smart_pos_vendor_portal.portal_my_stock_request",values)