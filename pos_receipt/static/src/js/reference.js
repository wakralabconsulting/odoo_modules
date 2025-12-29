/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useState, Component, xml,onMounted } from "@odoo/owl";



patch(PaymentScreen.prototype, {


    setup() {
        super.setup();
        this.orm = useService("orm");
 this.customNote = "";
        this.state = useState({
            payment_seq: null,
        });
    },

    async onMounted() {
        await this.fetchPaymentSequence();
    },

    async fetchPaymentSequence() {
        const seq = await this.orm.call(
            "pos.config",
            "getorder_name",
            [[],  this.pos.config.id]
        );

        this.state.payment_seq = seq;

        // store in order
        this.currentOrder.set_order_conf(seq);
    },

    updateCustomNote(ev) {
        this.customNote = ev.target.value;
        this.currentOrder.set_custom_note(this.customNote);
    }
});
