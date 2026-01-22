{
    'name': 'WEHA Smart POS - Multi Branch',
    'version': '16.0.1.0',
    'description': 'Multi Branch',
    'summary': 'Multi Branch',
    'author': 'WEHA',
    'website': 'https://www.weha-id.com',
    'license': 'LGPL-3',
    'category': 'POS',
    'depends': [
        'point_of_sale',    
        'multi_branch_base',
        'multi_branch_pos',        
    ],
    'data': [
        'views/res_branch_view.xml'
    ],
    'auto_install': False,
    'application': False,
    'assets': {
        
    }
}