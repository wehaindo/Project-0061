# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class PosActivityLogDashboard(models.Model):
    _name = "pos.activity.log.dashboard"
    _description = 'POS Activity Log Dashboard'
    
    name = fields.Char('Dashboard Name', default='POS Activity Dashboard')
    
    @api.model
    def get_dashboard_data(self, date_from=None, date_to=None, pos_config_ids=None, user_ids=None):
        """
        Get comprehensive dashboard data for activity logs
        """
        domain = []
        
        # Date filters
        if date_from:
            domain.append(('timestamp', '>=', date_from))
        if date_to:
            domain.append(('timestamp', '<=', date_to))
        
        # POS Config filter
        if pos_config_ids:
            domain.append(('pos_config_id', 'in', pos_config_ids))
        
        # User filter
        if user_ids:
            domain.append(('user_id', 'in', user_ids))
        
        # Get all logs matching criteria
        logs = self.env['pos.activity.log'].search(domain)
        
        # Calculate statistics
        total_activities = len(logs)
        
        # Group by activity type
        activity_by_type = {}
        for log in logs:
            activity_type = log.name
            if activity_type not in activity_by_type:
                activity_by_type[activity_type] = 0
            activity_by_type[activity_type] += 1
        
        # Top users
        user_activity = {}
        for log in logs:
            user_name = log.user_id.name if log.user_id else 'Unknown'
            if user_name not in user_activity:
                user_activity[user_name] = 0
            user_activity[user_name] += 1
        
        top_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Top POS Configs
        config_activity = {}
        for log in logs:
            config_name = log.pos_config_id.name if log.pos_config_id else 'Unknown'
            if config_name not in config_activity:
                config_activity[config_name] = 0
            config_activity[config_name] += 1
        
        top_configs = sorted(config_activity.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Activity timeline (by day)
        timeline_data = {}
        for log in logs:
            date_key = log.timestamp.strftime('%Y-%m-%d') if log.timestamp else 'Unknown'
            if date_key not in timeline_data:
                timeline_data[date_key] = 0
            timeline_data[date_key] += 1
        
        timeline_sorted = sorted(timeline_data.items())
        
        # Recent activities (last 20)
        recent_logs = logs.sorted(key=lambda r: r.timestamp, reverse=True)[:20]
        recent_activities = [{
            'id': log.id,
            'name': log.name,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if log.timestamp else '',
            'user': log.user_id.name if log.user_id else 'Unknown',
            'employee': log.hr_employee_id.name if log.hr_employee_id else '',
            'pos_config': log.pos_config_id.name if log.pos_config_id else '',
            'pos_session': log.pos_session_id.name if log.pos_session_id else '',
            'details': log.details or '',
        } for log in recent_logs]
        
        return {
            'total_activities': total_activities,
            'activity_by_type': [{'name': k, 'count': v} for k, v in activity_by_type.items()],
            'top_users': [{'name': u[0], 'count': u[1]} for u in top_users],
            'top_configs': [{'name': c[0], 'count': c[1]} for c in top_configs],
            'timeline': [{'date': t[0], 'count': t[1]} for t in timeline_sorted],
            'recent_activities': recent_activities,
        }
    
    @api.model
    def get_activity_stats(self):
        """
        Get quick statistics for dashboard tiles
        """
        today = fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        total = self.env['pos.activity.log'].search_count([])
        today_count = self.env['pos.activity.log'].search_count([('timestamp', '>=', today)])
        week_count = self.env['pos.activity.log'].search_count([('timestamp', '>=', week_ago)])
        month_count = self.env['pos.activity.log'].search_count([('timestamp', '>=', month_ago)])
        
        return {
            'total': total,
            'today': today_count,
            'this_week': week_count,
            'this_month': month_count,
        }
    
    @api.model
    def export_activity_logs(self, date_from=None, date_to=None, pos_config_ids=None, user_ids=None):
        """
        Export activity logs based on filters
        """
        domain = []
        
        if date_from:
            domain.append(('timestamp', '>=', date_from))
        if date_to:
            domain.append(('timestamp', '<=', date_to))
        if pos_config_ids:
            domain.append(('pos_config_id', 'in', pos_config_ids))
        if user_ids:
            domain.append(('user_id', 'in', user_ids))
        
        logs = self.env['pos.activity.log'].search(domain, order='timestamp desc')
        
        data = []
        for log in logs:
            data.append({
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if log.timestamp else '',
                'activity_type': log.name,
                'user': log.user_id.name if log.user_id else '',
                'employee': log.hr_employee_id.name if log.hr_employee_id else '',
                'pos_config': log.pos_config_id.name if log.pos_config_id else '',
                'pos_session': log.pos_session_id.name if log.pos_session_id else '',
                'pos_order': log.pos_order_reference or '',
                'details': log.details or '',
            })
        
        return data
