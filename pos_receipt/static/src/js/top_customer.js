/** @odoo-module **/
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { PosDB } from "@point_of_sale/app/store/db";
patch(PosDB.prototype, {

    setup() {
        super.setup(...arguments);




    },


    get_partners_sorted(max_count) {


        var shor = this.partner_sorted
        var list2 =[]
        max_count = max_count
            ? Math.min(this.partner_sorted.length, max_count)
            : this.partner_sorted.length;
        var partners = [];
        var top_pa = []
        var top_pa_fa = []
        for (var i = 0; i < max_count; i++) {
            console.log("this.partner_by_id[this.partner_sorted[i]]['top_customer']")
            if (this.partner_by_id[this.partner_sorted[i]]['top_customer']){
                top_pa.push(this.partner_by_id[this.partner_sorted[i]]['id'])
            }else{
                top_pa_fa.push(this.partner_by_id[this.partner_sorted[i]]['id'])
            }
        }
         // Insert list2 at index 0
        list2.push(...top_pa_fa);
        list2.splice(0, 0, ...top_pa);
        for (var i = 0; i < max_count; i++) {
            partners.push(this.partner_by_id[list2[i]]);
        }
        return partners;
    },

});