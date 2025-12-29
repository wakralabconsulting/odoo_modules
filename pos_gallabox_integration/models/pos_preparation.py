from odoo import models, api

class PosPreparationOrder(models.Model):
    _inherit = 'pos_preparation.display.order'

    def action_done(self):
        res = super().action_done()
        # The logic to send WhatsApp when kitchen marks 'Done'
        for order in self:
            pos_order = order.pos_order_id
            if pos_order and pos_order.partner_id.mobile:
                self.env['gallabox.service'].send_whatsapp_template(
                    recipient_name=pos_order.partner_id.name,
                    recipient_phone=pos_order.partner_id.mobile,
                    template_name="order_ready_kds",
                    body_values={
                        "customer": pos_order.partner_id.name,
                        "order": pos_order.pos_reference
                    }
                )
        return res