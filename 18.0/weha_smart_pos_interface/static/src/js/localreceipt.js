/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { _t } from "@web/core/l10n/translation";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
   async printReceipt({
        basic = false,
        order = this.get_order(),
        printBillActionTriggered = false,
    } = {}) {
        console.log('printReceipt');
        const result = await this.printer.print(
            OrderReceipt,
            {
                data: this.orderExportForPrinting(order),
                formatCurrency: this.env.utils.formatCurrency,
                basic_receipt: basic,
            },
            { webPrintFallback: true }
        );
        if (!printBillActionTriggered) {
            order.nb_print += 1;
            if (typeof order.id === "number" && result) {
                await this.data.write("pos.order", [order.id], { nb_print: order.nb_print });
            }
        }
        return true;
    }
});