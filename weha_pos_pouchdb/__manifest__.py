
# -*- coding: utf-8 -*-
###############################################################################
#
#    Wahyu Hidayat <wahhid@gmail.com>
#
#    Copyright (c) All rights reserved:
#        (c) 2020  KOIN
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#    
#    Odoo and OpenERP is trademark of Odoo S.A.
#
###############################################################################
{
    'name': 'POS PouchDB',
    'summary': 'PouchDB Capability',
    'version': '14.0.1.0',
    'description': """
POS PouchDB
==============================================
POS PouchDB
    """,
    'author': 'KOIN',
    'website': 'http://www.weha-id.com/',

    'license': 'AGPL-3',
    'category': 'Point of sale',

    'depends': [
        'point_of_sale',
        'pos_cache',
    ],
    'data': [
        'data/pos_pouchdb_data.xml',
        'views/templates.xml',
        'views/pos_config_view.xml',
    ],
    'demo': [
    ],
    'js': [
    ],
    'css': [
    ],
    'qweb': [
    ],
    'images': [
    ],
    'test': [
    ],
    'installable': True
}
