# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PosDashboard(models.Model):
    _name = 'pos.dashboard'
    _description = 'POS Dashboard'

    @api.model
    def get_dashboard_data(self, period=7, store_id=False):
        """
        Get comprehensive dashboard data for store performance monitoring
        """
        current_date = fields.Datetime.now()
        start_date = current_date - timedelta(days=period)
        
        domain = [
            ('date_order', '>=', start_date),
            ('date_order', '<=', current_date),
            ('state', 'in', ['paid', 'done', 'posted', 'invoiced'])
        ]
        
        if store_id:
            domain.append(('branch_id', '=', store_id))
        
        # Get previous period for comparison
        prev_start_date = start_date - timedelta(days=period)
        prev_domain = domain.copy()
        prev_domain[0] = ('date_order', '>=', prev_start_date)
        prev_domain[1] = ('date_order', '<', start_date)
        
        return {
            'revenue': self._get_revenue_data(domain, prev_domain),
            'orders': self._get_orders_data(domain, prev_domain),
            'customers': self._get_customers_data(domain, prev_domain),
            'products': self._get_products_data(domain, prev_domain),
            'payments': self._get_payments_data(domain),
            'hourly': self._get_hourly_data(domain),
            'top_products': self._get_top_products(domain),
            'top_categories': self._get_top_categories(domain),
            'cashiers': self._get_cashier_performance(domain),
            'stores': self._get_store_comparison(start_date, current_date),
        }
    
    def _get_revenue_data(self, domain, prev_domain):
        """Calculate revenue metrics"""
        orders = self.env['pos.order'].search(domain)
        prev_orders = self.env['pos.order'].search(prev_domain)
        
        current_revenue = sum(orders.mapped('amount_total'))
        prev_revenue = sum(prev_orders.mapped('amount_total'))
        
        percentage = 0
        if prev_revenue > 0:
            percentage = ((current_revenue - prev_revenue) / prev_revenue) * 100
        
        return {
            'current': current_revenue,
            'previous': prev_revenue,
            'percentage': round(percentage, 2),
            'average_order': round(current_revenue / len(orders), 2) if orders else 0
        }
    
    def _get_orders_data(self, domain, prev_domain):
        """Calculate order metrics"""
        current_count = self.env['pos.order'].search_count(domain)
        prev_count = self.env['pos.order'].search_count(prev_domain)
        
        percentage = 0
        if prev_count > 0:
            percentage = ((current_count - prev_count) / prev_count) * 100
        
        return {
            'current': current_count,
            'previous': prev_count,
            'percentage': round(percentage, 2)
        }
    
    def _get_customers_data(self, domain, prev_domain):
        """Calculate customer metrics"""
        orders = self.env['pos.order'].search(domain)
        prev_orders = self.env['pos.order'].search(prev_domain)
        
        current_customers = len(set(orders.mapped('partner_id.id')))
        prev_customers = len(set(prev_orders.mapped('partner_id.id')))
        
        percentage = 0
        if prev_customers > 0:
            percentage = ((current_customers - prev_customers) / prev_customers) * 100
        
        # Calculate member transactions
        member_orders = orders.filtered(lambda o: o.partner_id and o.partner_id.id != 1)
        
        return {
            'current': current_customers,
            'previous': prev_customers,
            'percentage': round(percentage, 2),
            'members': len(member_orders),
            'member_percentage': round((len(member_orders) / len(orders) * 100), 2) if orders else 0
        }
    
    def _get_products_data(self, domain, prev_domain):
        """Calculate product metrics"""
        orders = self.env['pos.order'].search(domain)
        
        total_qty = sum(orders.mapped('lines.qty'))
        unique_products = len(set(orders.mapped('lines.product_id.id')))
        
        return {
            'total_items_sold': int(total_qty),
            'unique_products': unique_products,
            'avg_items_per_order': round(total_qty / len(orders), 2) if orders else 0
        }
    
    def _get_payments_data(self, domain):
        """Get payment method breakdown"""
        orders = self.env['pos.order'].search(domain)
        payments = self.env['pos.payment'].search([('pos_order_id', 'in', orders.ids)])
        
        payment_data = {}
        for payment in payments:
            method = payment.payment_method_id.name
            if method not in payment_data:
                payment_data[method] = 0
            payment_data[method] += payment.amount
        
        return payment_data
    
    def _get_hourly_data(self, domain):
        """Get sales by hour"""
        orders = self.env['pos.order'].search(domain)
        
        hourly_data = {}
        for order in orders:
            hour = order.date_order.hour
            if hour not in hourly_data:
                hourly_data[hour] = {'count': 0, 'amount': 0}
            hourly_data[hour]['count'] += 1
            hourly_data[hour]['amount'] += order.amount_total
        
        return hourly_data
    
    def _get_top_products(self, domain, limit=10):
        """Get top selling products"""
        orders = self.env['pos.order'].search(domain)
        
        product_data = {}
        for order in orders:
            for line in order.lines:
                product = line.product_id
                if product.id not in product_data:
                    product_data[product.id] = {
                        'name': product.name,
                        'qty': 0,
                        'amount': 0
                    }
                product_data[product.id]['qty'] += line.qty
                product_data[product.id]['amount'] += line.price_subtotal_incl
        
        # Sort by amount and get top N
        sorted_products = sorted(product_data.items(), key=lambda x: x[1]['amount'], reverse=True)
        return [{'id': k, **v} for k, v in sorted_products[:limit]]
    
    def _get_top_categories(self, domain, limit=10):
        """Get top selling categories"""
        orders = self.env['pos.order'].search(domain)
        
        category_data = {}
        for order in orders:
            for line in order.lines:
                category = line.product_id.pos_categ_id
                if not category:
                    continue
                if category.id not in category_data:
                    category_data[category.id] = {
                        'name': category.name,
                        'qty': 0,
                        'amount': 0
                    }
                category_data[category.id]['qty'] += line.qty
                category_data[category.id]['amount'] += line.price_subtotal_incl
        
        sorted_categories = sorted(category_data.items(), key=lambda x: x[1]['amount'], reverse=True)
        return [{'id': k, **v} for k, v in sorted_categories[:limit]]
    
    def _get_cashier_performance(self, domain):
        """Get cashier performance data"""
        orders = self.env['pos.order'].search(domain)
        
        cashier_data = {}
        for order in orders:
            cashier = order.user_id
            if cashier.id not in cashier_data:
                cashier_data[cashier.id] = {
                    'name': cashier.name,
                    'orders': 0,
                    'amount': 0
                }
            cashier_data[cashier.id]['orders'] += 1
            cashier_data[cashier.id]['amount'] += order.amount_total
        
        sorted_cashiers = sorted(cashier_data.items(), key=lambda x: x[1]['amount'], reverse=True)
        return [{'id': k, **v} for k, v in sorted_cashiers]
    
    def _get_store_comparison(self, start_date, end_date):
        """Get store comparison data"""
        stores = self.env['res.branch'].search([])
        
        store_data = []
        for store in stores:
            orders = self.env['pos.order'].search([
                ('branch_id', '=', store.id),
                ('date_order', '>=', start_date),
                ('date_order', '<=', end_date),
                ('state', 'in', ['paid', 'done', 'posted', 'invoiced'])
            ])
            
            store_data.append({
                'id': store.id,
                'name': store.name,
                'orders': len(orders),
                'amount': sum(orders.mapped('amount_total')),
                'avg_order': round(sum(orders.mapped('amount_total')) / len(orders), 2) if orders else 0
            })
        
        return sorted(store_data, key=lambda x: x['amount'], reverse=True)
    
    @api.model
    def get_daily_chart_data(self, period=7, store_id=False):
        """Get daily sales data for charts"""
        current_date = fields.Datetime.now()
        start_date = current_date - timedelta(days=period)
        
        labels = []
        data = []
        
        for i in range(period + 1):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            
            labels.append(date.strftime('%d-%m-%Y'))
            
            domain = [
                ('date_order', '>=', date),
                ('date_order', '<', next_date),
                ('state', 'in', ['paid', 'done', 'posted', 'invoiced'])
            ]
            
            if store_id:
                domain.append(('branch_id', '=', store_id))
            
            orders = self.env['pos.order'].search(domain)
            data.append(sum(orders.mapped('amount_total')))
        
        return {
            'labels': labels,
            'data': data
        }
    
    @api.model
    def get_store_chart_data(self, period=7):
        """Get store comparison chart data"""
        current_date = fields.Datetime.now()
        start_date = current_date - timedelta(days=period)
        
        stores = self.env['res.branch'].search([])
        
        labels = []
        datasets = []
        
        # Generate date labels
        for i in range(period + 1):
            date = start_date + timedelta(days=i)
            labels.append(date.strftime('%d-%m-%Y'))
        
        # Generate data for each store
        for store in stores:
            data = []
            for i in range(period + 1):
                date = start_date + timedelta(days=i)
                next_date = date + timedelta(days=1)
                
                orders = self.env['pos.order'].search([
                    ('branch_id', '=', store.id),
                    ('date_order', '>=', date),
                    ('date_order', '<', next_date),
                    ('state', 'in', ['paid', 'done', 'posted', 'invoiced'])
                ])
                
                data.append(sum(orders.mapped('amount_total')))
            
            datasets.append({
                'label': store.name,
                'data': data
            })
        
        return {
            'labels': labels,
            'datasets': datasets
        }
