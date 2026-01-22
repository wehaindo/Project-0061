{
    "name": "POS Session Report Advance | POS Session Z Report | POS Z Report |  POS Session Report from front and Backend in Odoo POS | POS Cash register Z-Report in Odoo",
    "description": """Using this module you can print POS Z Session Report from front and Backend in odoo POS""",
    'summary': 'Using this module you can print POS Z Session Report from front and Backend in odoo POS.',
    'category': 'Point of Sale',    
    'version': '16.5.4.3',
    'sequence': 1,
    "author" : "DOTSPRIME",
    "email": 'dotsprime@gmail.com',
    'price': 15,
    "currency": "EUR",
    "license": 'AGPL-3',
    "depends": [
        "base",
        "point_of_sale",
        "weha_smart_pos_aeon_activity_log"
    ],
    "data": [
        "report/report_pos_session.xml",
        "views/pos_session_view.xml",
    ],
    'assets': {
        'point_of_sale.assets': [
            'sc_pos_session_z_report_advance/static/src/js/**/*',
            'sc_pos_session_z_report_advance/static/src/xml/**/*',
        ],
    },
    'demo': [],
    'images': ['static/description/main_screenshot.jpg'],  
    "live_test_url" : "https://youtu.be/LTXn34y0s00",       
    'installable': True,
    'auto_install': False,
    'application': True,
}
