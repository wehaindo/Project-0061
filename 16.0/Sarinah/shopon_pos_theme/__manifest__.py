{
    'name': 'ShopOn POS Theme',
    'version': '16.0.0.2',
    'summary': """
        ShopOn POS Theme, all in one pos, pos theme, pos layout, pos custome, pos stock, receipt, product information,
        pos order, pos cashin cashout, pos order, pos visibility control, product suggestion, hide out of stock product,
        point of sale theme, pos report, product stock, pos community, Odoo POS theme, Point of Sale Odoo, Odoo POS customization,
        Odoo POS templates, Odoo POS app, Odoo POS integration, Odoo POS module, Odoo POS plugins, Odoo POS user interface,
        Odoo POS layout, Odoo POS features, Odoo POS performance, Odoo POS, Point of Sale application, Retail management system,
        Inventory management, Offline mode support, Mobile POS, Customizable receipts, Order management,
        Point of Sale (POS) software, Retail POS system, POS software features, Order management, POS customization,
        POS system updates, Point of Sale (POS) software, POS in Odoo, Point of Sale in Odoo, POS theme in Odoo, odoo theme,
        responsive pos theme, pos interface, advanced pos theme, delight pos theme,
        """,
    'images': ['static/description/banner.png'],
    'description': 'ShopOn POS Theme',
    'category': 'Point of Sale',
    'author': 'Setu Consulting Services Pvt. Ltd.',
    'website': 'https://www.setuconsulting.com/',
    'support' : 'support@setuconsulting.com',
    'maintainer': 'Setu Consulting Services Private Limited',
    'license': 'OPL-1',
    'price': 0,
    'currency': 'EUR',
    'depends': ["point_of_sale","pos_hr"],

    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/pos_product_template_view.xml',
        'demo/pos_receipt_views_demo.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'shopon_pos_theme/static/src/js/**/*.js',
            'shopon_pos_theme/static/src/scss/pos_theme.scss',
            'shopon_pos_theme/static/src/scss/add_to_cart.scss',
            'shopon_pos_theme/static/src/xml/**/*.xml',
            ('before', 'point_of_sale/static/src/scss/pos_variables_extra.scss', 'shopon_pos_theme/static/src/scss/pos_variables_extra.scss'),
            'shopon_pos_theme/static/src/js/Chrome.js',
            'shopon_pos_theme/static/src/xml/Chrome.xml',
        ]
    },
    'installable': True,
    'auto_install': False,
    'uninstall_hook': 'uninstall_hook',
    'application': True,
}
