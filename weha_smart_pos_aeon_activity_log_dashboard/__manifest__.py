{
    "name": "WEHA Smart POS - AEON Activity Log Dashboard",
    "version": "16.0.1.0",
    "category": "Point of Sale",
    "depends": [
        'point_of_sale',
        'pos_hr',
        'web',
        'weha_smart_pos_aeon_activity_log',
    ],
    "author": "WEHA",
    "summary": "Dashboard for POS Activity Logs with Analytics and Reports",
    "description": """
POS Activity Log Dashboard
==========================

Features:
---------
* Real-time activity monitoring
* Statistical analysis and charts
* Activity breakdown by type, user, session
* Time-based filters (Today, This Week, This Month, Custom Range)
* Export functionality
* Detailed activity reports
* Top users and sessions analytics
* Activity trends visualization

This module provides comprehensive dashboard for monitoring and analyzing POS activity logs.
    """,
    "website": "https://www.weha-id.com",
    "email": "weha.consultant@gmail.com",
    "price": 0,
    "currency": "USD",
    "images": ["static/description/main_background.png"],
    "data": [
        'security/ir.model.access.csv',
        'views/pos_activity_log_dashboard_views.xml',
        'views/pos_activity_log_views.xml',
        'views/menu_views.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "weha_smart_pos_aeon_activity_log_dashboard/static/src/js/dashboard.js",
            "weha_smart_pos_aeon_activity_log_dashboard/static/src/xml/dashboard.xml",
            "weha_smart_pos_aeon_activity_log_dashboard/static/src/css/dashboard.css",
        ],
    },
    "auto_install": False,
    "installable": True,
    "license": "LGPL-3",
}
