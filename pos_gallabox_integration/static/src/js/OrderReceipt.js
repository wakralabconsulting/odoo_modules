/** @odoo-module **/
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";

patch(OrderReceipt.prototype, {
    setup() {
        super.setup();
        // This pulls the sequence/tracking number from the order data
        // so that props.track works in your XML
        this.track_no = this.props.data.track_no || this.props.data.name || "";
    },
    // This forces Odoo to use your custom XML template instead of the default one
    get template() {
        return "pos_gallabox_integration.GallaboxTorbaReceipt";
    }
});