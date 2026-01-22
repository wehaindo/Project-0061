
from odoo import http
from odoo.http import request
import base64

class ConsignmentPortal(http.Controller):

    @http.route(['/my/consignments'], type='http', auth="user", website=True)
    def portal_consignments(self, **kw):
        partner = request.env.user.partner_id
        contracts = request.env['consignment.contract'].sudo().search([('partner_id','=', partner.id)])
        values = {'contracts': contracts}
        return request.render("pos_consignment.portal_my_consignments", values)

    @http.route(['/my/consignments/<int:contract_id>/sales'], type='http', auth="user", website=True)
    def portal_contract_sales(self, contract_id, **kw):
        partner = request.env.user.partner_id
        contract = request.env['consignment.contract'].sudo().browse(contract_id)
        if not contract or contract.partner_id.id != partner.id:
            return request.redirect('/my')
        sales = request.env['pos.consignment.sale'].sudo().search([('contract_id','=', contract.id)])
        values = {'contract': contract, 'sales': sales}
        return request.render("pos_consignment.portal_contract_sales", values)

    @http.route(['/my/consignments/<int:contract_id>/settlements'], type='http', auth="user", website=True)
    def portal_contract_settlements(self, contract_id, **kw):
        partner = request.env.user.partner_id
        contract = request.env['consignment.contract'].sudo().browse(contract_id)
        if not contract or contract.partner_id.id != partner.id:
            return request.redirect('/my')
        settlements = request.env['consignment.settlement'].sudo().search(
            [('contract_id', '=', contract.id)], order='period_to desc'
        )
        values = {'contract': contract, 'settlements': settlements}
        return request.render("pos_consignment.portal_contract_settlements", values)

    @http.route(['/my/consignment/settlement/<int:settlement_id>/download'], type='http', auth="user")
    def portal_download_settlement(self, settlement_id, **kw):
        partner = request.env.user.partner_id
        settlement = request.env['consignment.settlement'].sudo().browse(settlement_id)
        if not settlement or settlement.contract_id.partner_id.id != partner.id:
            return request.redirect('/my')
        if settlement.pdf_statement:
            pdfdata = base64.b64decode(settlement.pdf_statement)
            filename = settlement.pdf_filename or f"consignment_settlement_{settlement.id}.pdf"
            return request.make_response(pdfdata, [
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ])
        else:
            pdf, filename = settlement.generate_pdf_report()
            return request.make_response(pdf, [
                ('Content-Type', 'application/pdf'),
                ('Content-Disposition', f'attachment; filename="{filename}"')
            ])
