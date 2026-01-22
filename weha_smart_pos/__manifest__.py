# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'WEHA - Smart Pos',
    'summary': """Smart Point of Sale""",
    'version': '14.0.0.1.0',
    'license': 'AGPL-3',
    'category': 'Point of sale',
    'author': 'WEHA',
    'website': 'https://www.weha-id.com',
    'depends': ['base','account','stock'],
    'data': [
        'data/ir_config_param.xml',
        'data/weha_smart_pos_data.xml',
        'security/weha_smart_pos_security.xml',
        'security/ir.model.access.csv',
        'views/weha_smart_pos_menu.xml',
        'views/product_templates_view.xml',
        'views/res_partner_view.xml',
        'views/res_users_view.xml',
        'views/weha_smart_pos_dashboard.xml',
        'views/weha_smart_pos_config_view.xml',
        'views/weha_smart_pos_payment_method_view.xml',      
        'views/weha_smart_pos_note_view.xml',              
        # 'views/weha_smart_pos_session_view.xml',
        'views/weha_smart_pos_wallet_view.xml',  
        'views/weha_smart_pos_order_view.xml',        
        'views/weha_smart_pos_templates.xml'
    ],
    'application': True,
    'installable': True,
    "auto_install": False,
}
