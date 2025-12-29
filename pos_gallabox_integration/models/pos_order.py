from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model_create_multi
    def create(self, vals_list):
        orders = super(PosOrder, self).create(vals_list)
        for order in orders:
            if order.config_id.whatsapp_enabled and order.partner_id.mobile:
                try:
                    # Use sudo to ensure we have permission to generate tokens
                    order.sudo().action_send_whatsapp_receipt()
                except Exception as e:
                    _logger.error("WhatsApp Trigger Error: %s", str(e))
        return orders

    def action_send_whatsapp_receipt(self):
        self.ensure_one()
        try:
            # 1. Get Base URL (ngrok link)
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/')
            
            # 2. FORCE Token Generation
            # This is the "Key" that stops the 303 Redirect to /web/login
            if not self.access_token:
                self.sudo()._portal_ensure_token()
            
            # 3. Construct the URL
            # Use the 'report_name' from your XML (pos_gallabox_integration.report_receipt_template_view)
            report_name = "pos_gallabox_integration.report_receipt_template_view"
            
            # We add ngrok-skip-browser-warning=1 to bypass the ngrok landing page
            pdf_url = f"{base_url}/report/pdf/{report_name}/{self.id}?access_token={self.access_token}&ngrok-skip-browser-warning=1"
            # ONLY add the bypass if we are actually using ngrok (Local Testing)
            if "ngrok" in base_url:
                pdf_url += "&ngrok-skip-browser-warning=1"
            # 4. LOG THE LINK FOR MANUAL TESTING
            # Check your terminal for this exact line!
            print("**************************************************")
            print("TEST THIS LINK IN INCOGNITO: %s", pdf_url)
            print("**************************************************")

            unique_num = self.session_id.sudo().receipt_sequence or self.name

            # 5. Send to Gallabox
            return self.env['gallabox.service'].sudo().send_whatsapp_template(
                recipient_name=self.partner_id.name or "Customer",
                recipient_phone=self.partner_id.mobile,
                template_name="order_confirmation_message_pos_reciept_utility_v4",
                body_values={
                    # "customer_name": self.partner_id.name or "Customer",
                    "1": str(unique_num),
                    # "order_reference": self.pos_reference,
                    "2": self.date_order.strftime('%d-%b-%Y %I:%M %p')
                },
                pdf_url=pdf_url,
                pdf_name=f"Receipt_{unique_num}.pdf"
            )
        except Exception as e:
            _logger.error("WhatsApp Action Error: %s", str(e))
            return False