{
    'name': 'WEHA - AEON Pos Dashboard',
    'version': '16.0.1.0',
    'description': 'WEHA - AEON Pos Dashboard',
    'summary': 'WEHA - AEON Pos Dashboard',
    'author': 'WEHA',
    'website': 'https://www.weha-id.com',
    'license': 'LGPL-3',
    'category': 'Point of sale',
    'depends': [
        'point_of_sale'
    ],
    'data': [
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