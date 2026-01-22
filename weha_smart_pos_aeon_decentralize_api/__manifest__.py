{
    "name" : "WEHA Smart POS - AEON Decentralize API",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : [
        'point_of_sale',
        'multi_branch_base',
        'weha_smart_pos_aeon_pos_data',
        'weha_smart_pos_aeon_pms',
        'weha_smart_pos_aeon_price',
        'weha_smart_pos_aeon_promotion',
        'weha_smart_pos_aeon_sku',
        'weha_smart_pos_aeon_multiple_barcode',
        'weha_smart_pos_aeon_multi_uom',        
        'weha_smart_pos_aeon_api',
        'weha_upload_transpos'
    ],
    "author": "WEHA",
    'summary': 'WEHA SMart POS Decentralize',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [
        'security/ir.model.access.csv',
        'wizards/wizard_generate_download_item_view.xml',
        'views/pos_decentralize_view.xml'
    ],
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}