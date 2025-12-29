/** @odoo-module **/

import { Order,Orderline } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

import { PosStore, register_payment_method } from "@point_of_sale/app/store/pos_store";


patch(Order.prototype, {

    set_order_conf(value) {
        this.order_conf = value;
    },

    get_order_conf() {
        return this.order_conf || "";
    },

    set_custom_note(value) {
        this.custom_note = value;
    },

    get_custom_note() {
        return this.custom_note;
    },

    export_as_JSON() {
        const json = super.export_as_JSON();
        json.custom_note = this.custom_note;
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(json);
        this.custom_note = json.custom_note;
    },

    export_for_printing() {
        const result = super.export_for_printing();
        result.custom_note = this.custom_note;
        result.order_conf = this.order_conf;
//        result.kkkkkkkkkk = this.loadOrderConf();
        console.log("aaaaaaaaaaaaaaaaaaaaaaaaaaa", result, this.name)
        return result;
    },



});


patch(Orderline.prototype, {


   getDisplayData() {
        console.log("a666666666666",this.get_product(), this.get_product().id)
        return {
            productName: this.get_full_product_name(),
            price: this.getPriceString(),
            qty: this.get_quantity_str(),
            categ_id_data : this.get_product().categ,
            unit: this.get_unit().name,
            unitPrice: this.env.utils.formatCurrency(this.get_unit_display_price()),
            oldUnitPrice: this.env.utils.formatCurrency(this.get_old_unit_display_price()),
            discount: this.get_discount_str(),
            customerNote: this.get_customer_note(),
            internalNote: this.getNote(),
            comboParent: this.comboParent?.get_full_product_name(),
            pack_lot_lines: this.get_lot_lines(),
            price_without_discount: this.env.utils.formatCurrency(
                this.getUnitDisplayPriceBeforeDiscount()
            ),
            attributes: this.attribute_value_ids
                ? this.findAttribute(this.attribute_value_ids, this.custom_attribute_value_ids)
                : [],
        }
    }


});
