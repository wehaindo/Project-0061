# -*- coding: utf-8 -*-
# from odoo import http


# class McsAsplPosPromotionResPartner(http.Controller):
#     @http.route('/mcs_aspl_pos_promotion_res_partner/mcs_aspl_pos_promotion_res_partner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mcs_aspl_pos_promotion_res_partner/mcs_aspl_pos_promotion_res_partner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mcs_aspl_pos_promotion_res_partner.listing', {
#             'root': '/mcs_aspl_pos_promotion_res_partner/mcs_aspl_pos_promotion_res_partner',
#             'objects': http.request.env['mcs_aspl_pos_promotion_res_partner.mcs_aspl_pos_promotion_res_partner'].search([]),
#         })

#     @http.route('/mcs_aspl_pos_promotion_res_partner/mcs_aspl_pos_promotion_res_partner/objects/<model("mcs_aspl_pos_promotion_res_partner.mcs_aspl_pos_promotion_res_partner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mcs_aspl_pos_promotion_res_partner.object', {
#             'object': obj
#         })
