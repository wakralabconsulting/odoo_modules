from odoo import models, fields, api
import requests
import logging

_logger = logging.getLogger(__name__)

class GallaboxService(models.Model):
    _name = 'gallabox.service'
    _description = 'Gallabox WhatsApp Service'

    @api.model
    def send_whatsapp_template(self, recipient_name, recipient_phone, template_name, body_values, pdf_url=None, pdf_name="Receipt"):
        params = self.env['ir.config_parameter'].sudo()
        api_key = params.get_param('pos_gallabox.api_key')
        api_secret = params.get_param('pos_gallabox.api_secret')
        channel_id = params.get_param('pos_gallabox.channel_id')

        payload = {
            "channelId": channel_id,
            "channelType": "whatsapp",
            "recipient": {"name": recipient_name, "phone": recipient_phone},
            "whatsapp": {
                "type": "template",
                "template": {
                    "templateName": template_name,
                    "bodyValues": body_values 
                }
            }
        }

        if pdf_url:
            payload["whatsapp"]["template"]["headerValues"] = {
                "mediaUrl": pdf_url,
                "mediaName": pdf_name
            }

        headers = {
            'apiKey': api_key,
            'apiSecret': api_secret,
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'  # This is the magic line
        }
        
        try:
            # TERMINAL LOG FOR API CALL
            print("\n" + "*"*60)
            print("STEP 3: SENDING TO GALLABOX SERVER")
            print(f"URL: https://server.gallabox.com/devapi/messages/whatsapp")
            print("*"*60 + "\n")

            response = requests.post(
                'https://server.gallabox.com/devapi/messages/whatsapp', 
                json=payload, 
                headers=headers,
                timeout=15
            )
            
            # TERMINAL LOG FOR RESPONSE
            print(f"RESULT: Status {response.status_code}")
            print(f"RESPONSE BODY: {response.text}")
            
            return response.json()
        except Exception as e:
            _logger.error("Gallabox Connection Error: %s", str(e))
            print(f"CRITICAL API ERROR: {str(e)}")
            return {"status": "error", "message": str(e)}