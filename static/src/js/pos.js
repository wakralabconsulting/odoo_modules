/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order,Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";


patch(Order.prototype, {

    set_custom_note(note) {
        this.custom_note = note;
    },

    get_custom_note(order) {
        return order.custom_note;
    },

    export_as_JSON() {
        const json = super.export_as_JSON();
        json.custom_note = this.custom_note;
        return json;
    },
});



/** @odoo-module **/



