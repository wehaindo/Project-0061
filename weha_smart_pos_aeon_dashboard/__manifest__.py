{
    'name': 'WEHA - AEON Pos Dashboard',
    'version': '16.0.2.0',
    'description': 'WEHA - AEON Pos Dashboard - Comprehensive Store Performance Monitoring',
    'summary': 'WEHA - AEON Pos Dashboard with KPIs, Charts, and Analytics',
    'author': 'WEHA',
    'website': 'https://www.weha-id.com',
    'license': 'LGPL-3',
    'category': 'Point of sale',
    'depends': [
        'point_of_sale',
        'multi_branch_base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_dashboard_view.xml',
    ],    
    'auto_install': False,
    'application': False,
    'assets': {
        'web.assets_backend': [
            'weha_smart_pos_aeon_dashboard/static/src/components/**/*.js',
            'weha_smart_pos_aeon_dashboard/static/src/components/**/*.xml',
            'weha_smart_pos_aeon_dashboard/static/src/components/**/*.scss',
        ],
    }
}