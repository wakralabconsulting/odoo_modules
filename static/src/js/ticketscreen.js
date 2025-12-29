/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";


patch(TicketScreen.prototype, {


    _getSearchFields() {
        const fields = {
            TRACKING_NUMBER: {
                repr: (order) => order.trackingNumber,
                displayName: _t("Order Number"),
                modelField: "tracking_number",
            },
            TRACKING_NUMBER: {
                repr: (order) => order.custom_note,
                displayName: _t("Customer Reference"),
                modelField: "custom_note",
            },
            RECEIPT_NUMBER: {
                repr: (order) => order.name,
                displayName: _t("Receipt Number"),
                modelField: "pos_reference",
            },
            DATE: {
                repr: (order) => formatDateTime(order.date_order),
                displayName: _t("Date"),
                modelField: "date_order",
                formatSearch: (searchTerm) => {
                    const includesTime = searchTerm.includes(':');
                    let parsedDateTime;
                    try {
                        parsedDateTime = parseDateTime(searchTerm);
                    } catch {
                        return searchTerm;
                    }
                    if (includesTime) {
                        return parsedDateTime.toUTC().toFormat("yyyy-MM-dd HH:mm:ss");
                    } else {
                        return parsedDateTime.toFormat("yyyy-MM-dd");
                    }
                }
            },
            PARTNER: {
                repr: (order) => order.get_partner_name(),
                displayName: _t("Customer"),
                modelField: "partner_id.complete_name",
            },
        };

        if (this.showCardholderName()) {
            fields.CARDHOLDER_NAME = {
                repr: (order) => order.get_cardholder_name(),
                displayName: _t("Cardholder Name"),
                modelField: "payment_ids.cardholder_name",
            };
        }

        return fields;
    },

    _getOrderList() {
        this.pos.get_order_list().sort((a, b) => new Date(b.date_order) - new Date(a.date_order));
        return this.pos.get_order_list();
    }


});
