from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self, orders, draft=False):
        # 1. Standard Odoo logic first
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        
        # 2. Extract IDs safely
        actual_ids = [o['id'] if isinstance(o, dict) else o for o in order_ids]
        created_orders = self.sudo().browse(actual_ids)

        for order in created_orders:
            # SAFETY CHECK: Only proceed if fields exist and are set
            config = order.config_id
            if hasattr(config, 'whatsapp_enabled') and config.whatsapp_enabled:
                # Check for the design field specifically
                design = getattr(config, 'whatsapp_receipt_design_id', False)
                if design and order.partner_id.mobile:
                    _logger.info("GALLABOX: Triggering WhatsApp for %s", order.name)
                    order.action_send_whatsapp_receipt()
        
        return order_ids

    def action_send_whatsapp_receipt(self):
        self.ensure_one()
        try:
            # 1. Correct the Base URL (Important!)
            # Based on your image_6cbc49.png, this is still 'localhost'.
            # We will fix the setting below, but the code will use whatever is in Settings.
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/')
            
            if not self.access_token:
                self.sudo()._portal_ensure_token()
            
            # 2. Use the External ID from your views/report_receipt_template.xml 
            report_id = "pos_gallabox_integration.action_report_pos_receipt"
            
            pdf_url = f"{base_url}/report/pdf/{report_id}/{self.id}?access_token={self.access_token}"
            
            # Bypass ngrok warning for the API
            if "ngrok" in base_url:
                pdf_url += "&ngrok-skip-browser-warning=1"

            print("**************************************************")
            print("TEST THIS LINK IN INCOGNITO: %s", pdf_url)
            print("**************************************************")

            # 3. Call the Gallabox Service
            return self.env['gallabox.service'].sudo().send_whatsapp_template(
                recipient_name=self.partner_id.name or "Customer",
                recipient_phone=self.partner_id.mobile,
                template_name="order_confirmation_message_pos_reciept_utility_v4",
                body_values={
                    "1": str(self.pos_reference or self.name),
                    "2": self.date_order.strftime('%d-%b-%Y %I:%M %p')
                },
                pdf_url=pdf_url,
                pdf_name=f"Receipt_{self.name}.pdf"
            )
        except Exception as e:
            _logger.error("Gallabox Error: %s", str(e))
            return False