{
    "name" : "WEHA Smart POS - AEON POS Data Cleaning",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale','weha_smart_pos_aeon_pos_data'],
    "author": "WEHA",
    'summary': 'Automated CouchDB Data Cleaning for Expired Pricelists',
    "description": """
        WEHA Smart POS - AEON POS Data Cleaning
        ========================================
        
        Automated cleanup of expired product pricelist items from CouchDB.
        
        Features:
        ---------
        * Automated daily cleanup of expired pricelists from CouchDB
        * Configurable retention period (default: 7 days after expiry)
        * Manual cleanup option for administrators
        * Only cleans CouchDB data, preserves Odoo database records
        * Detailed logging of all cleanup operations
        * Multi-branch support
        
        Purpose: Optimize CouchDB storage by removing expired pricelist data
                 while maintaining historical records in Odoo database.
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/product_product_view.xml',
        'views/product_pricelist_view.xml',
        'views/res_config_settings_view.xml',
    ],
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}