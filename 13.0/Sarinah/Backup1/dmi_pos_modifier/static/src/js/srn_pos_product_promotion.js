odoo.define('dmi_pos_modifier.pos_custom_discount', function (require) {
    'use strict';

    var models = require('point_of_sale.models');
    var screens = require("point_of_sale.screens");
    var rpc = require('web.rpc');
    var core = require('web.core');
    var QWeb = core.qweb;

    screens.ReceiptScreenWidget.include({

        get_receipt_render_env: async function () {
            var render_env = this._super();

            // Handle referral codes
            var refferal2 = self.glob_pos_referral_code2;
            // Inisialisasi untuk perhitungan diskon
            if (refferal2 && refferal2[this.pos.get_order().cid]) {
                render_env.refferal2 = refferal2[this.pos.get_order().cid].referral_code2_name || '';
            } else {
                render_env.refferal2 = this.pos.get_order().refferal_name2 || '';
            }

            // Mendapatkan referral dari glob_pos_referral_code jika ada
            var refferal = self.glob_pos_referral_code;
            // Inisialisasi untuk perhitungan diskon
            if (refferal && refferal[this.pos.get_order().cid]) {
                render_env.refferal = refferal[this.pos.get_order().cid].referral_code_name || '';
            } else {
                render_env.refferal = this.pos.get_order().refferal_name || '';
            }

            // Menyimpan nilai ke order
            this.pos.get_order().refferal_name2 = render_env.refferal2;
            this.pos.get_order().refferal_name = render_env.refferal;

            console.log("get_receipt_render_env new rpc")
            // Fetch discounts from the database
            var fetchProductDiscounts = async () => {
                // var current_date = new Date();
                var current_date = moment(new Date()).locale('en').format("YYYY-MM-DD");
                var weekday = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
                var d = new Date();
                var current_day = weekday[d.getDay()]
                try {
                    return await rpc.query({
                        model: 'srn.pos.product.discount',
                        method: 'search_read',
                        domain: [
                            ['available_in_receipt', '=', true],
                            ['date_from', '<=', current_date],
                            ['day_of_week_ids.name', 'in', [current_day]],
                            ['date_to', '>=', current_date],
                        ],
                        fields: ['id','name', 'available_in_receipt', 'date_from', 'date_to', 'terms_text', 'min_amount_show','sku','type_scan','pos_config_ids','max_amount_show'],
                        order: 'min_amount_show desc',
                    });
                } catch (error) {
                    console.error('Failed to fetch discounts:', error);
                    return [];
                }
            };

            const getDateServer = async () => {
                try {
                    const dateServer = await rpc.query({
                        model: 'pos.order',
                        method: 'get_date_server',
                    });
                    return dateServer;
                } catch (error) {
                    console.error('Failed to fetch server date:', error);
                    return null; // Return null to indicate failure
                }
            };

            const serverDate = await getDateServer();

            // Apply discount logic
            var applyDiscount = async () => {
                var subtotal = this.pos.get_order().get_subtotal();
                var discounts = await fetchProductDiscounts();

                // Find applicable discount
                var applicableDiscount = discounts
                .filter(discount =>
                    subtotal >= discount.min_amount_show &&
                    subtotal <= discount.max_amount_show &&
                    discount.pos_config_ids.includes(this.pos.config_id)
                )
                .reduce((maxDiscount, currentDiscount) =>
                    !maxDiscount || currentDiscount.min_amount_show > maxDiscount.min_amount_show
                        ? currentDiscount
                        : maxDiscount,
                    null
                );

                if (applicableDiscount) {
                    console.log('Applicable Discount:', applicableDiscount);
                } else {
                    console.log('No applicable discounts found.');
                }

                return applicableDiscount;
            };


            // Wait for the discount application and update the render environment
            var pos_product_discount_apply = await applyDiscount();
            render_env.pos_product_discount_apply = pos_product_discount_apply || null;
            render_env.date_server = serverDate

            console.log('get_receipt_render_env executed successfully.');
            return render_env;

//            return {
//                widget: this,
//                pos: this.pos,
//                order: order,
//                receipt: order.export_for_printing(),
//                orderlines: order.get_orderlines(),
//                paymentlines: order.get_paymentlines(),
//            };
        },
        render_receipt: async function() {
                console.log('receipt-------------------------------');
                this.$('.pos-receipt-container').html(QWeb.render('OrderReceipt', await this.get_receipt_render_env()));
                console.log('-------------receipt');
            },

    });


    // Load model 'srn.pos.product.discount' with active = True
    models.load_models({
        model: 'srn.pos.product.discount',
        fields: ['id','name', 'available_in_receipt', 'date_from', 'date_to', 'terms_text', 'min_amount_show','sku','type_scan','pos_config_ids'],
        domain: function (self) {
            var current_date = moment(new Date()).locale('en').format("YYYY-MM-DD");
            var weekday = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
            var d = new Date();
            var current_day = weekday[d.getDay()]
            // var current_date = new Date();
            return [['available_in_receipt', '=', true],['day_of_week_ids.name', 'in', [current_day]], ['date_from', '<=', current_date], ['date_to', '>=', current_date]];
        },
        loaded: function (self, pos_product_discount) {
            self.pos_product_discount = pos_product_discount;
        },
    });

    var _super = models.Orderline;
    models.Orderline = models.Orderline.extend({
        export_for_printing: function () {
            var json = _super.prototype.export_for_printing.apply(this, arguments);
            var promotion_list = this.pos.pos_promotions;
            var promotion = promotion_list.find(promo => promo.id === this.custom_promotion_id)
            json.discount_amt = this.discount_amt
            json.default_code = this.get_product().default_code;
            json.barcode = this.get_product().barcode;
            if (promotion) {
                json.promotion_code = promotion.promotion_code;
            } else {
                json.promotion_code = "";
            }
            var base_price_product = this.get_product().get_price(this.pos.get_order().pricelist, 1);
            var total_base_price = base_price_product * this.get_quantity();
            var total_discount_price = total_base_price - json.price_display;
            json.total_base_price = total_base_price;
            json.base_price_product = base_price_product;
            json.total_discount_price = total_discount_price;



            console.log("export_for_printing custom 1")
            return json;
        },
    });

    models.Orderline = models.Orderline.extend({
        export_for_printing: function () {
            var json = _super.prototype.export_for_printing.apply(this, arguments);
            var promotion_list = this.pos.pos_promotions;
            var promotion = promotion_list.find(promo => promo.id === this.custom_promotion_id)
            json.discount_amt = this.discount_amt
            json.default_code = this.get_product().default_code;
            json.barcode = this.get_product().barcode;
            if (promotion) {
                json.promotion_code = promotion.promotion_code;
            } else {
                json.promotion_code = "";
            }
            var base_price_product = this.get_product().get_price(this.pos.get_order().pricelist, 1);
            var total_base_price = base_price_product * this.get_quantity();
            var total_discount_price = total_base_price - json.price_display;
            json.total_base_price = total_base_price;
            json.base_price_product = base_price_product;
            json.total_discount_price = total_discount_price;



            console.log("export_for_printing custom 1")
            return json;
        },
    });

});
