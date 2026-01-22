{
    "name" : "WEHA Smart POS - POS BCA EDC",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'Intgrate with BCA EDC / ECR',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 10.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        # 'views/res_config_settings_view.xml',
    ],
     'assets': {
        'point_of_sale.assets': [
            # 'weha_smart_pos_base/static/src/css/screen.css',
            # 'wahe_smart_pos_bca_edc/static/lib/connect.js',
            'weha_smart_pos_bca_edc/static/src/js/**/*.js',
            'weha_smart_pos_bca_edc/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}