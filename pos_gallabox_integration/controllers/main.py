from odoo import http
from odoo.http import request

class PosWhatsappController(http.Controller):

    @http.route(['/pos/receipt/pdf/<int:order_id>'], type='http', auth='public', website=True)
    def get_pos_pdf_receipt(self, order_id, **kwargs):
        # Find the order (using sudo to bypass login requirements)
        order = request.env['pos.order'].sudo().browse(order_id)
        if not order.exists():
            return request.not_found()

        # Generate the PDF
        pdf_content, _ = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'point_of_sale.report_receipt', [order.id]
        )

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', 'inline; filename="receipt.pdf"'),
        ]
        return request.make_response(pdf_content, headers=pdfhttpheaders)