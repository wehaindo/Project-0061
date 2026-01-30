# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json


class PosActivityLogDashboardController(http.Controller):
    
    @http.route('/pos_activity_log/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self, date_from=None, date_to=None, pos_config_ids=None, user_ids=None):
        """
        Get dashboard data via JSON RPC
        """
        dashboard_model = request.env['pos.activity.log.dashboard']
        return dashboard_model.get_dashboard_data(
            date_from=date_from,
            date_to=date_to,
            pos_config_ids=pos_config_ids,
            user_ids=user_ids
        )
    
    @http.route('/pos_activity_log/stats', type='json', auth='user')
    def get_stats(self):
        """
        Get quick statistics
        """
        dashboard_model = request.env['pos.activity.log.dashboard']
        return dashboard_model.get_activity_stats()
    
    @http.route('/pos_activity_log/export', type='json', auth='user')
    def export_logs(self, date_from=None, date_to=None, pos_config_ids=None, user_ids=None):
        """
        Export activity logs
        """
        dashboard_model = request.env['pos.activity.log.dashboard']
        return dashboard_model.export_activity_logs(
            date_from=date_from,
            date_to=date_to,
            pos_config_ids=pos_config_ids,
            user_ids=user_ids
        )
