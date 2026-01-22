# -*- coding: utf-8 -*-
#################################################################################
# Author      : WEHA Consultant (<www.weha-id.com>)
# Copyright(c): 2015-Present WEHA Consultant.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from odoo import api, fields, models
import json
from odoo import http
from odoo.http import request


class VendorProduct(http.Controller):
    @http.route('/vendor/create_product', type="http", auth="user")
    def create_product(self, name, sku, unit_measure, product_categories, **kwargs):        
        res = request.env['product.template'].sudo().create({
            'name': name,
            # 'image_1920': image,
            'detailed_type': 'product',
            'default_code': sku,
            'list_price': 0.0,
            # 'uom_id': int(unit_measure),
            # 'uom_po_id': int(unit_measure),
            'pos_categ_id': int(product_categories),
            'available_in_pos': True,
            # 'barcode': barcode,
        })

    @http.route('/portal-product-category-data', type='json', auth='user', website=True)
    def portal_product_category_data(self, **kw):
        dic = {}
        if kw.get('category_id') and kw.get('category_id') != 'category':
            
            sub_categ_list = []
            sub_categ_ids = request.env['helpdesk.subcategory'].sudo().search(
                [('parent_category_id', '=', int(kw.get('category_id')))])
            for sub in sub_categ_ids:
                sub_categ_dic = {
                    'id': sub.id,
                    'name': sub.name,
                }
                sub_categ_list.append(sub_categ_dic)
            dic.update({
                'sub_categories': sub_categ_list
            })
        else:
            dic.update({
                'sub_categories': []
            })
        return json.dumps(dic)

    @http.route('/portal-product-uom-data', type='json', auth='user', website=True)
    def portal_product_uom_data(self, **kw):
        dic = {}
        if kw.get('product_uom_id') and kw.get('product_uom_id') != 'uom_id':
            pass
        dic.update({
            'product_uoms': []
        })

    @http.route('/portal-create-ticket', type='http', auth='public', csrf=False)
    def portal_create_ticket(self, **kw):
        try:
            multi_users_value = request.httprequest.form.getlist('portal_assign_multi_user')
            if 'users' in multi_users_value:
                del multi_users_value[0]
            login_user = request.env.user
            if login_user and login_user.login != 'public':
                partner_id = False
                if kw.get('partner_id') and kw.get('partner_id') != '':
                    partner_id = request.env['res.partner'].sudo().search(
                        [('id', '=', int(kw.get('partner_id')))], limit=1)
                else:
                    partner_id = request.env['res.partner'].sudo().search(
                        [('email', '=', kw.get('portal_email'))], limit=1)
                if not partner_id:
                    partner_id = request.env['res.partner'].sudo().create({
                        'name': kw.get('portal_contact_name'),
                        'company_type': 'person',
                        'email': kw.get('portal_email'),
                    })
                if partner_id:
                    ticket_dic = {'partner_id': partner_id.id,
                                  'ticket_from_portal': True}
                    if len(multi_users_value) > 0:
                        users = []
                        for user in multi_users_value:
                            users.append(int(user))
                        multi_users = request.env['res.users'].sudo().browse(users)
                        if multi_users:
                            ticket_dic.update({
                                'sh_user_ids': [(6,0,multi_users.ids)]
                            })
                    if kw.get('portal_team') and kw.get('portal_team') != 'team':
                        team_id = request.env['helpdesk.team'].sudo().browse(
                            int(kw.get('portal_team')))
                        if team_id:
                            ticket_dic.update({
                                'team_id': team_id.id,
                                'team_head': team_id.team_head.id,
                            })
                    if kw.get('portal_assign_user') and kw.get('portal_assign_user') != 'user':
                        portal_user_id = request.env['res.users'].sudo().browse(
                            int(kw.get('portal_assign_user')))
                        if portal_user_id:
                            ticket_dic.update({
                                'user_id': portal_user_id.id,
                            })
                    if not ticket_dic.get('team_id') or not ticket_dic.get('user_id'):
                        if login_user.sh_portal_user_access and request.env.user.has_group('base.group_portal') and login_user.sh_portal_user_access == 'user' or login_user.sh_portal_user_access == 'manager' or login_user.sh_portal_user_access == 'leader':
                            if request.env.company.sh_default_team_id:
                                ticket_dic.update({
                                    'team_id': request.env.company.sh_default_team_id.id,
                                    'team_head': request.env.company.sh_default_team_id.team_head.id,
                                    'user_id': request.env.company.sh_default_user_id.id,
                                })
                            else:
                                team_id = request.env['helpdesk.team'].sudo().search(
                                    ['|', ('team_head', '=', login_user.id), ('team_members', 'in', [login_user.id])])
                                if team_id:
                                    ticket_dic.update({
                                        'team_id': team_id[-1].id,
                                        'team_head': team_id[-1].team_head.id,
                                        'user_id': login_user.id,
                                    })
                                else:
                                    ticket_dic.update({
                                        'user_id': login_user.id,
                                    })
                            ticket_dic.update({'state': 'staff_replied'})
                        else:
                            if request.env.company.sh_default_team_id:
                                ticket_dic.update({
                                    'team_id': request.env.company.sh_default_team_id.id,
                                    'team_head': request.env.company.sh_default_team_id.team_head.id,
                                    'user_id': request.env.company.sh_default_user_id.id,
                                })
                            else:
                                if not login_user.has_group('base.group_portal') and not login_user.sh_portal_user_access:
                                    team_id = request.env['helpdesk.team'].sudo().search(
                                        ['|', ('team_head', '=', login_user.id), ('team_members', 'in', [login_user.id])])
                                    if team_id:
                                        ticket_dic.update({
                                            'team_id': team_id[-1].id,
                                            'team_head': team_id[-1].team_head.id,
                                            'user_id': login_user.id,
                                        })
                                    else:
                                        ticket_dic.update({
                                            'user_id': login_user.id,
                                        })
                    if kw.get('portal_contact_name'):
                        ticket_dic.update({
                            'person_name': kw.get('portal_contact_name'),
                        })
                    if kw.get('portal_email'):
                        ticket_dic.update({
                            'email': kw.get('portal_email'),
                        })
                    if kw.get('portal_category') and kw.get('portal_category') != 'category':
                        ticket_dic.update({
                            'category_id': int(kw.get('portal_category')),
                        })
                    if kw.get('portal_subcategory') and kw.get('portal_subcategory') != 'sub_category':
                        ticket_dic.update({
                            'sub_category_id': int(kw.get('portal_subcategory')),
                        })
                    if kw.get('portal_subject') and kw.get('portal_subject') != 'subject':
                        ticket_dic.update({
                            'subject_id': int(kw.get('portal_subject')),
                        })
                    if kw.get('portal_description'):
                        ticket_dic.update({
                            'description': kw.get('portal_description'),
                        })
                    if kw.get('portal_priority') and kw.get('portal_priority') != 'priority':
                        ticket_dic.update({
                            'priority': int(kw.get('portal_priority')),
                        })
                    ticket_id = request.env['helpdesk.ticket'].sudo().create(
                        ticket_dic)
                    if 'portal_file' in request.params:
                        attached_files = request.httprequest.files.getlist(
                            'portal_file')
                        attachment_ids = []
                        for attachment in attached_files:
                            result = base64.b64encode(attachment.read())
                            attachment_id = request.env['ir.attachment'].sudo().create({
                                'name': attachment.filename,
                                'res_model': 'helpdesk.ticket',
                                'res_id': ticket_id.id,
                                'display_name': attachment.filename,
                                'datas': result,
                            })
                            attachment_ids.append(attachment_id.id)
                        ticket_id.attachment_ids = [(6, 0, attachment_ids)]
            return werkzeug.utils.redirect("/my/tickets")
        except Exception as e:
            _logger.exception('Something went wrong %s',str(e))
            
