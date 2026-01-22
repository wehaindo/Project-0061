/** @odoo-module **/

import { Order, Orderline, PosGlobalState} from 'point_of_sale.models';
import Registries from 'point_of_sale.Registries';
import session from 'web.session';
import concurrency from 'web.concurrency';
import { Gui } from 'point_of_sale.Gui';
import { round_decimals,round_precision } from 'web.utils';
import core from 'web.core';

const _t = core._t;
const dropPrevious = new concurrency.MutexedDropPrevious(); // Used for queuing reward updates
const mutex = new concurrency.Mutex(); // Used for sequential cache updates


const PosLogoOrder = (Order) => class PosLogoOrder extends Order {

    setup() {
        super.setup(...arguments);
        console.log("Load POS Logo Order");
    }

    get_receipt_logo_url(){
        return window.location.origin + "/web/image?model=pos.config&field=pos_receipt_logo_img&id=" + this.pos.config.id;
    }

    get_receipt_global_logo_url(){
        return window.location.origin + "/web/image?model=res.company&field=pos_global_receipt_logo_img&id=" + this.pos.company.id;
    }

    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        // result.receipt_log_url_base64 = this.env.pos.config.pos_receipt_logo_img;
        result.is_show_receipt_logo = this.pos.config.is_show_receipt_logo;
        result.receipt_logo_url = this.get_receipt_logo_url();
        result.receipt_global_logo_url = this.get_receipt_global_logo_url();
        console.log(result);
        return result;
    }

}

Registries.Model.extend(Order, PosLogoOrder);
