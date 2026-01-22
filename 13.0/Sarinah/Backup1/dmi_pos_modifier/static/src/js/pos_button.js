odoo.define('dmi_pos_modifier.ReferralButton2', function (require) {
    'use strict';

    // Reuire POS Screens
    var pos_screens = require('point_of_sale.screens');
    // Require POS GUI
    var gui = require('point_of_sale.gui');
    // Require POS Popups
    var popups = require('point_of_sale.popups');
    // Require Web RPC
    var rpc = require('web.rpc');
    // Require POS Model
    var models = require('point_of_sale.models');
    // Load field pos_ref_code_id in model pos.order
    models.load_fields('pos.order', ['pos_ref_code2_id', 'refferal_name', 'refferal_name','pos_ref_code_id']);

    // global variable json
    var glob_pos_referral_code2 = {}


    // Create a new button by extending the base ActionButtonWidget
    var ReferralButton2 = pos_screens.ActionButtonWidget.extend({
        template: 'SrnReferralButton2',
        button_click: function () {
            // console.log('action widget');
            // console.log(this.pos);
            // alert('clicked');
            let _this = this;
            _this.pos.gui.show_popup('Referral-Code2-Popup')
        }
    });


    // Define the Referral Button Action Button
    pos_screens.define_action_button({
        'name': 'Referral-Code2-Btn',
        'widget': ReferralButton2,
        // 'condition': function () {
        //     return this.pos;
        // }
    });


    // Create a popup by extending popups
    var ReferalPopup2 = popups.extend({
        template: 'SrnReferralPopup2',
        events: _.extend({}, popups.prototype.events, {
            'click .button.cek-referral-code2': 'click_cek_referral_code2',
            'click .button.rem-referral-code2': 'click_rem_referral_code2'
        }),
        show: function (options) {
            this._super(options);
            // console.log(this);
            // console.log('popup opened');

            let label_ref_code2 = document.getElementById('label-refcode2');
            let current_referral_code2 = glob_pos_referral_code2[this.pos.get_order()['cid']];
            // console.log(_this.pos.get_order()['cid']);
            // console.log(glob_pos_referral_code2);
            // console.log(current_referral_code);
            // set label with selected referral code
            if (current_referral_code2) {
                label_ref_code2.innerText = current_referral_code2.referral_code2_name;
                // console.log(current_referral_code);
            }
        },
        click_cek_referral_code2: function () {
            let _this = this;
            let ref_code2 = document.getElementById('referral_code2');
            let label_ref_code2 = document.getElementById('label-refcode2');

            label_ref_code2.innerText = ref_code2.value;

            // cek input, tidak boleh kosong dan tidak boleh berisi space
            if (ref_code2.value == "") {
                label_ref_code2.innerText = "Silahkan masukan referral code !";
                return;
            }
            // cek input has symbol and space
            if (/[^a-zA-Z0-9]/gi.test(ref_code2.value)) {
                label_ref_code2.innerText = "Referral Code tidak boleh ada spasi atau simbol !"
                return;
            }


            // cek client offline 
            if (!window.navigator.onLine) {
                label_ref_code2.innerText = "Tidak ada koneksi internet, silahkan coba beberapa saat lagi !";
                return;
            }

            label_ref_code2.innerText = "Loading ...";
            var model = 'pos.referral.code2';
            // Use an empty array to search for all the records
            var domain = [['active', '=', true], ['code', '=', ref_code2.value]];
            // Use an empty array to read all the fields of the records
            var fields = [];
            rpc.query({
                model: model,
                method: 'search_read',
                args: [domain, fields],
            }).then(function (data) {
                // console.log(data);
                if (data.length > 0) {
                    // set label
                    label_ref_code2.innerText = data[0].name;

                    // set referral code to global variable
                    glob_pos_referral_code2[_this.pos.get_order()['cid']] = {
                        referral_code2_id: data[0].id,
                        referral_code2_code: data[0].code,
                        referral_code2_name: data[0].name
                    };
                    self.glob_pos_referral_code2 = glob_pos_referral_code2 ;

                    // console.log(glob_pos_referral_code2);

                    // remove element if existing
                    $(".yyt_display_referrence_code2").remove();
                    // add to display
                    $(".order-scroller").append(`<div class='yyt_display_referrence_code2'><span class='fa fa-link'></span> ${data[0].name}</div>`);
                    // console.log(glob_pos_referral_code2[_this.pos.get_order()['cid']]);
                } else {
                    label_ref_code2.innerText = 'Referral Code Not Found';
                }

            });

            // console.log(ref_code.value);

            // console.log(this.pos.get_order());

            // set referral_code for current order
            // glob_pos_referral_code2[this.pos.get_order()['cid']] = ref_code.value;
        },
        click_rem_referral_code2: function () {
            // console.log(glob_pos_referral_code2);
            delete glob_pos_referral_code2[this.pos.get_order()['cid']];
            // console.log(glob_pos_referral_code2);
            // console.log(this);
            $(".yyt_display_referrence_code2").remove();
            // close popup
            this.gui.close_popup();
            if (this.options.cancel) {
                this.options.cancel.call(this);
            }
        }
    });


    // Define Referral Popup
    gui.define_popup({
        'name': 'Referral-Code2-Popup',
        'widget': ReferalPopup2
    });


    // extend models order and override some function
    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        // override export_as_JSON, it call when payment lint clicked
        export_as_JSON: function () {
            var json = _super_order.export_as_JSON.apply(this, arguments);

            // set pos_referral_code to current_order json
            json.pos_ref_code2_id = glob_pos_referral_code2[this['cid']]?.referral_code2_id;
            return json;
        },
        // override finalize function
        finalize: function () {
            _super_order.finalize.apply(this, arguments);
            // delete referral code for current order
            delete glob_pos_referral_code2[this['cid']];
        }
    });


    // cegah display refcode ilang disini
    pos_screens.OrderWidget.include({
        renderElement: function () {
            this._super();
            // console.log('include order widget');
            if (glob_pos_referral_code2[this.pos.get_order()['cid']]) {
                let data = glob_pos_referral_code2[this.pos.get_order()['cid']]
                if ($('yyt_display_referrence_code2').length < 1) {
                    // add element kembali jika element hilang karena dirender saat menambahkan product/menghapus product
                    $(".order-scroller").append(`<div class='yyt_display_referrence_code2'><span class='fa fa-link'></span> ${data.referral_code2_name}</div>`);
                }
            }
        }
    });

});