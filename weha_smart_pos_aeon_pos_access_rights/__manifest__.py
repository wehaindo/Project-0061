{
    "name" : "WEHA Smart POS - AEON POS Access Rights",
    "version" : "16.0.1.0",
    "category" : "Point of Sale",
    "depends" : ['point_of_sale',
                 'pos_hr',
                 'multi_branch_base',
                 'weha_smart_pos_login',
                 'weha_smart_pos_aeon_activity_log'
    ],
    "author": "WEHA",
    'summary': 'POS Access Rights',
    "description": """
        Purpose : POS 
    """,
    "website" : "https://www.weha-id.com",
    'email': "weha.consultant@gmail.com",
    'price': 0,
    'currency': 'USD',
    'images': ['static/description/main_background.png'],
    "data": [        
        'views/res_config_settings_view.xml',
        'views/res_branch_view.xml',
        'views/hr_employee_view.xml'
    ],
    'assets': {
        "web.assets_backend": [
            "weha_smart_pos_aeon_pos_access_rights/static/src/js/Dialog/FingerDialogAction.js",
            "weha_smart_pos_aeon_pos_access_rights/static/src/js/Dialog/FingerDialog.js",
            "weha_smart_pos_aeon_pos_access_rights/static/src/xml/Dialog/FingerDialog.xml",
        ],
        'point_of_sale.assets': [
            "weha_smart_pos_aeon_pos_access_rights/static/src/js/models.js",
            "weha_smart_pos_aeon_pos_access_rights/static/src/css/style.css",
            "weha_smart_pos_aeon_pos_access_rights/static/src/js/Popup/FingerprintAuthPopup.js",
            "weha_smart_pos_aeon_pos_access_rights/static/src/js/Popup/ClosePosPopup.js",
            "weha_smart_pos_aeon_pos_access_rights/static/src/js/Popup/EmployeeGridPopup.js",
            "weha_smart_pos_aeon_pos_access_rights/static/src/js/Popup/SupervisorGridPopup.js",
            "weha_smart_pos_aeon_pos_access_rights/static/src/js/Screen/LoginScreen.js",
            "weha_smart_pos_aeon_pos_access_rights/static/src/js/HeaderLockButton.js",
            "weha_smart_pos_aeon_pos_access_rights/static/src/xml/Popup/FingerprintAuthPopup.xml",            
            "weha_smart_pos_aeon_pos_access_rights/static/src/xml/Popup/ClosePosPopup.xml",                                    
            "weha_smart_pos_aeon_pos_access_rights/static/src/xml/Popup/EmployeeGridPopup.xml",                                    
            "weha_smart_pos_aeon_pos_access_rights/static/src/xml/Popup/SupervisorGridPopup.xml",                                    
            "weha_smart_pos_aeon_pos_access_rights/static/src/xml/Screen/LoginScreen.xml",
            "weha_smart_pos_aeon_pos_access_rights/static/src/xml/CashierName.xml",
            
        ],
    },
    "auto_install": False,
    "installable": True,
    'license': 'LGPL-3',
}