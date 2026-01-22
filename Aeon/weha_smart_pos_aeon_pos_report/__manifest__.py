{
    'name': 'WEHA - AEON POS Report',
    'version': '16.0.0.1',
    'description': 'Reporting',
    'summary': 'WEHA - AEON POS Report',
    'author': 'WEHA',
    'website': 'www.weha-id.com',
    'license': 'LGPL-3',
    'category': 'Point of Sale',
    'images': ['static/description/main_background.png'],
    'depends': [
        'point_of_sale', 
        'report_xlsx',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/wizard_pos_payment_report_view.xml',
        'wizards/wizard_product_template_report_view.xml',
        'wizards/wizard_pos_order_line_report_view.xml',
        'reports/pos_payment_report_template.xml',
        'reports/product_template_report_template.xml',
        'reports/pos_order_line_report_template.xml',
    ],
    'demo': [
        ''
    ],
    'auto_install': False,
    'application': False,
    'assets': {
        'point_of_sale.assets': [
            'weha_smart_pos_aeon_pos_report/static/lib/**/*.js',
            'weha_smart_pos_aeon_pos_report/static/src/js/**/*.js',
            'weha_smart_pos_aeon_pos_report/static/src/xml/**/*.xml',
        ],
    },
}