/** @odoo-module */
import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";
import { useState, Component, xml,onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

patch(OrderReceipt.prototype, {
    setup() {
    super.setup();

    this.pos = useService("pos");

    this.state = useState({
        template: true,
            order_conf: null,
    });


},



    get templateProps() {
        var paart = "";
        var mobile = "";

        if (this.props.data?.partner?.name) {
            paart = this.props.data.partner.name;
            mobile = this.props.data.partner.mobile;
        }

        var numb = this.props.data.name;
        if (numb) {
            var numb4 = numb.slice(-4);
            numb = parseInt(numb4);
        }

        let lastPart = this.props.data.name.split("-").pop();
                    let num = parseInt(lastPart) || 0;
        let track = String(num % 100).padStart(1, "0");

        const categoryWiseLines = {};
        var line_cou = [1, 2];
        var nn = 2;

        this.props.data.orderlines.forEach(line => {
            const catName = line?.categ_id_data?.name || "Uncategorized";

            if (!categoryWiseLines[catName]) {
                categoryWiseLines[catName] = [];
                nn += 1;
                line_cou.push(nn);
            }
            categoryWiseLines[catName].push(line);
        });
        let num2 = parseInt(track) || 0;
        let orderConf = parseInt(this.pos.config.namm, 10) || 0;
        console.log("nare-----------", orderConf)
        // 🔥 Get reactive value from state
        const names_v = orderConf + num2;
        console.log("--------------",names_v, this.pos.orders)
        return {
            pos: this.pos,
            num: numb,
            party_m: mobile,
            party: paart,
            a2: window.location.origin + '/web/image?model=pos.config&field=pos_logo&id=' + this.pos.config.id,
            data: this.props.data,
            order: this.pos.orders,
            order_conf : this.props.data.order_conf,
            custom_note: this.props.data.custom_note,
            categoryWise: categoryWiseLines,
            line_c: line_cou,
            track: track,
            name_h: names_v,   // <-- value now available safely
            receipt: this.props.data,
            orderlines: this.props.data.orderlines,
            paymentlines: this.props.data.paymentlines,
        };


    },

    get templateComponent() {
        var mainRef = this;
        return class extends Component {
            static template = xml`${mainRef.pos.config.design_receipt}`;
        };
    },

    get isTrue() {
        return !this.env.services.pos.config.is_custom_receipt;
    },
});
