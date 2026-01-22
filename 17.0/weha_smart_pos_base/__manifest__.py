{
    "name" : "WEHA Smart POS - POS Base",
    "version" : "17.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale'],
    "author": "WEHA",
    'summary': 'Improve Several Features for Point of Sale',
    "description": """
        Purpose : Improve more features for Point of sale 
        Feature : 1.  Customize POS Theme Layout
                  2.  Hide and Show Product Grid
                  Maximize Orderline layout
                  4.  Enable Supervisor Approval for Some Access Rights
                  5.  Shopping Bag Charging
                  6.  Setup Default Customer for Orders
                  7.  Support Multiple Barcode for Product
                  Support Multiple UOM for Product
                  9.  Improve Customer Display with Carousel
                  Add Custom Receipt Logo
                  Loyalty
                  12. Support Payment Method Popup                  
                  13. Voucher, Selling Voucher and Reward(Coupon)                  
                  14. Deposit, Topup/Refund and Payment
                  15. Promotion, Loyalty and Reward
                  16. Support Send Message to POS Session from Backend
                  17. Support POS Support Complaint Request using Odoo Discuss
                  18. Support Direct Login and Logout
                  19. Support Price Checker to help customer check product price
                  Support Order Queue Display
                  21. Push or Pull Sync for Product and Customer From Backend to POS
                  22. Support Backup Order Locally and Sync Certain Backup Order Locally to Server
                  23. Support Sync Backup Order using CouchDB (only support with multi branch) (comming soon)                                 
                  24. Support Recover missing orders using CouchDB  (only support with multi branch) (comming soon)             
                  25. Change current Order workflow Using CouchDB (only support with multi branch) (comming soon)
                  26. Interface Application for Serial Port (only support with multi branch) (comming soon)
                  27. Integrate with WEHA Smart POS Android Version (only support with multi branch) (comming soon)                  
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 85.00,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',        
        'data/base_sequence.xml',
        'wizards/wizard_send_message_view.xml',
        'views/weha_smart_pos_base_menu.xml',
        'views/direct_login_templates.xml',
        'views/pos_config_view.xml',
        'views/res_config_settings_view.xml',
        'views/pos_session_views.xml',
        'views/product_views.xml',
        'views/discuss_channel_views.xml',
        'views/res_partner_view.xml',
        'views/pos_deposit_view.xml',
        'views/pos_voucher_views.xml',
        'views/pos_promotion_views.xml',
        'views/pos_payment_method_view.xml'
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_smart_pos_base/static/lib/js/pouchdb-8.0.1.min.js',
            'weha_smart_pos_base/static/lib/js/pouchdb.find.js',
            'weha_smart_pos_base/static/src/**/*',            
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}