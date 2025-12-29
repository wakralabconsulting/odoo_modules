from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Global Gallabox Settings
    gallabox_api_key = fields.Char(string="Gallabox API Key", config_parameter='pos_gallabox.api_key')
    gallabox_api_secret = fields.Char(string="Gallabox API Secret", config_parameter='pos_gallabox.api_secret')
    gallabox_channel_id = fields.Char(string="Gallabox Channel ID", config_parameter='pos_gallabox.channel_id')
    
    # Links the setting to the specific POS
    pos_whatsapp_enabled = fields.Boolean(related='pos_config_id.whatsapp_enabled', readonly=False)