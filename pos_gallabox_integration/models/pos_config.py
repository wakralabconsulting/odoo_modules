from odoo import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    whatsapp_enabled = fields.Boolean(string="WhatsApp Enabled", default=False)