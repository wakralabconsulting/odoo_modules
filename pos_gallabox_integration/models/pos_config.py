from odoo import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'

    whatsapp_enabled = fields.Boolean(string="Enable WhatsApp Notifications")
    whatsapp_receipt_design_id = fields.Many2one(
        'pos.receipt',  # Changed from 'pos.receipt.design' to 'pos.receipt'
        string="WhatsApp Receipt Design",
        ondelete='set null'
    )