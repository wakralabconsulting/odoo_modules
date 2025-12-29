/** @odoo-module **/

import { Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
patch(Orderline.prototype, {
    setup() {
        super.setup(...arguments);
    this.internalNote = this.product.lst_price.toString();
    this.note = this.product.lst_price.toString();
    console.log("aaaaaaaaaaaaaaaaaaa", this)

    },
});