from odoo import models, api, fields
import logging

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _process_order_results(self, order_results):
        """ This method runs when POS syncs orders to the server """
        # 1. Run the standard Odoo process first
        res = super(PosOrder, self)._process_order_results(order_results)
        
        # 2. Get the IDs of the orders that were just created
        order_ids = [r['id'] for r in order_results if 'id' in r]
        orders = self.browse(order_ids)

        for order in orders:
            _logger.info("========== GALLABOX DEBUG START ==========")
            _logger.info("Order: %s", order.name)
            
            # Check if WhatsApp is enabled in the POS Config settings
            whatsapp_enabled = order.config_id.whatsapp_enabled 
            has_phone = order.partner_id.mobile or order.partner_id.phone

            if whatsapp_enabled and has_phone:
                try:
                    _logger.info("Triggering WhatsApp receipt for %s", has_phone)
                    order.sudo().action_send_whatsapp_receipt()
                except Exception as e:
                    _logger.error("Gallabox Error: %s", str(e))
            else:
                _logger.warning("Skipped: Enabled=%s, Phone=%s", whatsapp_enabled, has_phone)
            
            _logger.info("========== GALLABOX DEBUG END ===========")
            
        return res

    def action_send_whatsapp_receipt(self):
        self.ensure_one()
        # Ensure token exists for external PDF access
        if not self.access_token:
            self.sudo()._portal_ensure_token()
            
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/')
        report_name = "pos_gallabox_integration.report_receipt_template_view"
        
        # Construct the URL with ngrok bypass
        pdf_url = f"{base_url}/report/pdf/{report_name}/{self.id}?access_token={self.access_token}"
        if "ngrok" in base_url:
            pdf_url += "&ngrok-skip-browser-warning=1"

        # Unique number logic
        unique_num = self.pos_reference or self.name

        return self.env['gallabox.service'].sudo().send_whatsapp_template(
            recipient_name=self.partner_id.name or "Customer",
            recipient_phone=self.partner_id.mobile or self.partner_id.phone,
            template_name="order_confirmation_message_pos_reciept_utility_v4",
            body_values={
                "1": str(unique_num),
                "2": self.date_order.strftime('%d-%b-%Y %I:%M %p')
            },
            pdf_url=pdf_url,
            pdf_name=f"Receipt_{unique_num}.pdf"
        )