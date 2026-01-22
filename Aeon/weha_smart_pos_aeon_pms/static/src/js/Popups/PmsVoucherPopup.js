odoo.define('weha_smart_pos_aeon_pms.PmsVoucherPopup', function(require) {
    'use strict';

    const { onMounted, useRef, useState } = owl;
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    class PmsVoucherPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            this.state = useState({ VoucherFull: '', VoucherNumber: '', VoucherAmount:0.0, ShowMsg: false, Valid: true});
            this.voucherNumberRef = useRef('vouchernumber');
            onMounted(this.onMounted);
        }

        onMounted() {
            this.voucherNumberRef.el.focus();
        }

        async searchVoucher(){
            // 0 0 0 0 2 0 0 0 3 4 2 2 1 2 0 0 0 0 6 4 4 7 0 8
            // 000020003422120000644708
            var self = this;
            this.state.ShowMsg = false;
            // var order = this.env.pos.get_order();
            // var today = moment().locale('en').format('YYYY-MM-DD');
            
            var voucher = self.state.VoucherNumber;
            var voucherAmount = voucher.substring(0,8);
            var voucherNumber = voucher.substring(8,24);
            this.state.VoucherFull = voucher;
            this.state.VoucherNumber = voucherNumber;
            this.state.VoucherAmount = parseInt(voucherAmount);
            this.state.Valid = true;
        }

        getPayload() {
            return {full: this.state.VoucherNumber, amount:this.state.VoucherNumber.substring(0,8), number:this.state.VoucherNumber.substring(8,24)};
        }
    }

    PmsVoucherPopup.template = 'PmsVoucherPopup';
    PmsVoucherPopup.defaultProps = {
        confirmText: 'Apply',
        cancelText: 'Cancel',
        title: '',
        body: '',
    };
    Registries.Component.add(PmsVoucherPopup);
    return PmsVoucherPopup;

});
