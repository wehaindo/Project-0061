{
    'name': 'WEHA Smart POS - Vendor Portal',
    'version': '16.0.1.0',
    'description': 'Vendor Portal',
    'summary': 'Vendor Portal',
    'author': 'WEHA',
    'website': 'https://www.weha-id.com',
    'license': 'LGPL-3',
    'category': 'Portal',
    'depends': [
        'vendor_portal_odoo',
        'stock_request'    
    ],
    'data': [
        'views/portal_vendor_templates.xml',
        'views/product_template_view.xml'
    ],    
     "assets": {        
        'web.assets_frontend':[
            "weha_smart_pos_vendor_portal/static/src/js/portal.js",
        ]
    },
    'auto_install': False,
    'application': False,    
}