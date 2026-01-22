odoo.define('weha_smart_pos_voucher.models', function (require) {
    "use strict";

    var { PosGlobalState, Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const GiftVoucherPosGlobalState = (PosGlobalState) => class GiftVoucherPosGlobalState extends PosGlobalState {
        constructor(obj) {
            super(obj);
        }
        async _processData(loadedData) {
            await super._processData(...arguments);
            this.gift_vouchers = loadedData['aspl.gift.voucher'];
            this.payment_method = await loadedData['pos.payment.method'];
            await this.loadGiftVoucher();
        }
        loadGiftVoucher(){
            this.giftVoucher_by_id = {};
            for(let type in this.gift_vouchers){
                this.giftVoucher_by_id[type.id] = type;
            }
        }

    }
    Registries.Model.extend(PosGlobalState, GiftVoucherPosGlobalState);

    const setGiftVoucher = (Order) => class setGiftVoucher extends Order {
        constructor(obj, options) {
            super(...arguments);
            this.redeem = [];
            this.redeem_order_count = 0;
        }
        export_as_JSON() {
               const json = super.export_as_JSON(...arguments);
               json.redeem = this.get_redeem_giftvoucher() || false;
                return json;
        }
        export_for_printing(){
             var orders = super.export_for_printing(...arguments);
             return orders;
        }
        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
        }
        set_redeem_giftvoucher(voucher) {
            this.redeem.push(voucher)
        }
        get_redeem_giftvoucher() {
            return this.redeem;
        }
        set_redemption_order_count(){
            this.redeem_order_count += 1;
        }
        get_redemption_order_count(){
            return this.redeem_order_count;
        }
    }
    Registries.Model.extend(Order, setGiftVoucher);
});