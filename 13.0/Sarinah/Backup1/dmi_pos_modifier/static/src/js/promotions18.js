odoo.define('dmi_pos_modifier.promotions', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var utils = require('web.utils');
    var gui = require('point_of_sale.gui');

    var rpc = require('web.rpc');

    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;


    models.PosModel.prototype.models.push(
        {
            model: 'pos.promotion',
            fields: [],
            domain: function (self) {
                var current_date = moment(new Date()).locale('en').format("YYYY-MM-DD");
                var weekday = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
                var current_time = moment(new Date().getTime()).locale('en').format("H");
                var d = new Date();
                var current_day = weekday[d.getDay()]
                return [['from_date', '<=', current_date], ['to_date', '>=', current_date], ['active', '=', true],
                ['day_of_week_ids.name', 'in', [current_day]], ['id', 'in', self.config.promotion_ids],
                ['state', '=', 'approved']
                ];
            },
            loaded: function (self, pos_promotions) {
                self.pos_promotions = pos_promotions;
            },
        }, {
        model: 'pos.conditions',
        fields: [],
        loaded: function (self, pos_conditions) {
            self.pos_conditions = pos_conditions;
        },
    }, {
        model: 'get.discount',
        fields: [],
        loaded: function (self, pos_get_discount) {
            self.pos_get_discount = pos_get_discount;
        },
    }, {
        model: 'quantity.discount',
        fields: [],
        loaded: function (self, pos_get_qty_discount) {
            self.pos_get_qty_discount = pos_get_qty_discount;
        },
    }, {
        model: 'quantity.discount.amt',
        fields: [],
        loaded: function (self, pos_qty_discount_amt) {
            self.pos_qty_discount_amt = pos_qty_discount_amt;
        },
    }, {
        model: 'discount.multi.products',
        fields: [],
        loaded: function (self, pos_discount_multi_prods) {
            self.pos_discount_multi_prods = pos_discount_multi_prods;
        },
    }, {
        model: 'discount.seasonal',
        fields: [],
        loaded: function (self, pos_discount_seasonal) {
            self.pos_discount_seasonal = pos_discount_seasonal;
        },
    }, {
        model: 'discount.multi.categories',
        fields: [],
        loaded: function (self, pos_discount_multi_categ) {
            self.pos_discount_multi_categ = pos_discount_multi_categ;
        },
    }, {
        model: 'discount.above.price',
        fields: [],
        loaded: function (self, pos_discount_above_price) {
            self.pos_discount_above_price = pos_discount_above_price;
        },
    });

    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            this.is_bxgy = false;
            this.list_ori_bxgy = null;
            _super_Order.initialize.call(this, attributes, options);
        },
        export_as_JSON: function () {
            var json = _super_Order.export_as_JSON.apply(this, arguments);
            json.is_bxgy = this.is_bxgy || false;
            json.list_ori_bxgy = this.list_ori_bxgy || null;
            return json;
        },
        export_for_printing: function () {
            var self = this;
            var orders = _super_Order.export_for_printing.call(this);
            var new_val = {
                is_bxgy: this.is_bxgy || false,
                list_ori_bxgy: this.list_ori_bxgy || null,
            };
            $.extend(orders, new_val);

            console.log("export_for_printing ordersss")
            return orders;
        },
        apply_promotion: function (change_value = true) {
            if (change_value) {
                var self = this;
                self.remove_promotion();
                var order = self.pos.get_order();
                var client = order.get_client();
                var lines = order.get_new_order_lines();
                if (order && lines && lines[0] && order.is_bxgy) {
                    _.each(lines, function (line) {
                        
                        if (order.list_ori_bxgy) {
                            _.each(order.list_ori_bxgy, function (final) {
                                if (line.product.id == final.product_id) {
                                    if (final.is_new_line) {
                                        line.set_quantity(final.new_qty + final.free_qty);
                                    }
                                }
                            });
                            
                        }
                    });
                    order.list_ori_bxgy = null;
                    order.is_bxgy = false;

                }
                var promotion_list = self.pos.pos_promotions;
                var condition_list = self.pos.pos_conditions;
                var discount_list = self.pos.pos_get_discount;
                var pos_get_qty_discount_list = self.pos.pos_get_qty_discount;
                var pos_qty_discount_amt = self.pos.pos_qty_discount_amt;
                var pos_discount_multi_prods = self.pos.pos_discount_multi_prods;
                var pos_discount_seasonal = self.pos.pos_discount_seasonal;
                var pos_discount_multi_categ = self.pos.pos_discount_multi_categ;
                var pos_discount_above_price = self.pos.pos_discount_above_price;
                var selected_line = self.pos.get_order().get_selected_orderline();
                var current_time = Number(moment(new Date().getTime()).locale('en').format("H"));
                if (order && lines && lines[0]) {
                    _.each(lines, function (line) {
                        if (promotion_list && promotion_list[0]) {
                            _.each(promotion_list, function (promotion) {
                                if ((Number(promotion.from_time) <= current_time && Number(promotion.to_time) > current_time) || (!promotion.from_time && !promotion.to_time)) {
                                    if (promotion && promotion.promotion_type == "buy_x_get_y") {
                                        if (promotion.pos_condition_ids && promotion.pos_condition_ids[0]) {
                                            _.each(promotion.pos_condition_ids, function (pos_condition_line_id) {
                                                var line_record = _.find(condition_list, function (obj) { return obj.id == pos_condition_line_id });
                                                if (line_record) {
                                                    if (line_record.product_x_id && line_record.product_x_id[0] && (jQuery.inArray(line.product.id, line_record.product_x_id) != -1)) {
                                                        line.free_product_x_id = line_record.id;
                                                        //if(!line.get_is_rule_applied()){
                                                        /*
                                                        if (line_record.operator == 'is_eql_to') {
                                                            if (line_record.quantity == line.quantity) {
                                                                if (line_record.product_y_id && line_record.product_y_id[0]) {
                                                                    var product = self.pos.db.get_product_by_id(line_record.product_y_id[0]);
                                                                    var new_line = new models.Orderline({}, { pos: self.pos, order: order, product: product });

                                                                    // MCS
                                                                    // new_line.fix_discount = new_line.price * line_record.quantity_y;
                                                                    // !MCS

                                                                    new_line.set_quantity(line_record.quantity_y);
                                                                    // new_line.set_unit_price(0);
                                                                    new_line.set_discount(100);
                                                                    new_line.set_promotion({
                                                                        'prom_prod_id': line_record.product_y_id[0],
                                                                        'parent_product_id': line_record.product_x_id[0],
                                                                        'rule_name': promotion.promotion_code,
                                                                    });
                                                                    new_line.set_is_rule_applied(true);

                                                                    // MCS
                                                                    new_line.custom_promotion_id = promotion.id;
                                                                    if (promotion.vendor_id && promotion.vendor_id[0]) {
                                                                        new_line.vendor_id = promotion.vendor_id[0];
                                                                    }
                                                                    new_line.vendor_shared = promotion.vendor_shared;
                                                                    new_line.sarinah_shared = promotion.sarinah_shared;
                                                                    //line.custom_promotion_id = promotion.id;
                                                                    // !MCS

                                                                    order.add_orderline(new_line);
                                                                    line.set_child_line_id(new_line.id);
                                                                    line.set_is_rule_applied(true);
                                                                }
                                                            }
                                                        }
                                                        else if (line_record.operator == 'greater_than_or_eql') {
                                                            if (line.quantity >= line_record.quantity) {

                                                                if (line_record.product_y_id && line_record.product_y_id[0]) {
                                                                    var product = self.pos.db.get_product_by_id(line_record.product_y_id[0]);
                                                                    var new_line = new models.Orderline({}, { pos : self.pos, order: order, product: product });
                                                                    console.log(new_line);

                                                                    // MCS
                                                                    // new_line.fix_discount = new_line.price * line_record.quantity_y;
                                                                    var new_qty = line_record.quantity_y;

                                                                    new_qty = new_qty * (Math.floor(line.quantity / line_record.quantity))

                                                                    new_line.set_quantity(new_qty);

                                                                    // !MCS

                                                                    // new_line.set_quantity(line_record.quantity_y);
                                                                    // new_line.set_unit_price(0);
                                                                    new_line.set_discount(100);
                                                                    new_line.set_promotion({
                                                                        'prom_prod_id': line_record.product_y_id[0],
                                                                        'parent_product_id': line_record.product_x_id[0],
                                                                        'rule_name': promotion.promotion_code,
                                                                    });

                                                                    new_line.set_is_rule_applied(true);
                                                                    order.add_orderline(new_line);
                                                                    line.set_child_line_id(new_line.id);
                                                                    line.set_is_rule_applied(true);

                                                                    // MCS
                                                                    new_line.custom_promotion_id = promotion.id;
                                                                    if (promotion.vendor_id && promotion.vendor_id[0]) {
                                                                        new_line.vendor_id = promotion.vendor_id[0];
                                                                    }
                                                                    new_line.vendor_shared = promotion.vendor_shared;
                                                                    new_line.sarinah_shared = promotion.sarinah_shared;
                                                                    // line.custom_promotion_id = promotion.id;
                                                                    // !MCS

                                                                }
                                                            }
                                                        }
                                                        */
                                                        //}
                                                    }
                                                    if (line_record.product_y_id && line_record.product_y_id[0] && (jQuery.inArray(line.product.id, line_record.product_y_id) != -1)) {
                                                        line.free_product_y_id = line_record.id;
                                                    }
                                                }
                                            });
                                        }
                                    }
                                    else if (promotion && promotion.promotion_type == "buy_x_get_dis_y") {
                                        if (promotion.parent_product_ids && promotion.parent_product_ids[0] && (jQuery.inArray(line.product.id, promotion.parent_product_ids) != -1)) {
                                            var disc_line_ids = [];
                                            _.each(promotion.pos_quntity_dis_ids, function (pos_quntity_dis_id) {
                                                var disc_line_record = _.find(discount_list, function (obj) { return obj.id == pos_quntity_dis_id });
                                                if (disc_line_record) {
                                                    if (disc_line_record.product_id_dis && disc_line_record.product_id_dis[0]) {
                                                        disc_line_ids.push(disc_line_record);
                                                    }
                                                }
                                            });
                                            line.set_buy_x_get_dis_y({
                                                'disc_line_ids': disc_line_ids,
                                                'promotion': promotion,
                                            });
                                        }
                                        if (line.get_buy_x_get_dis_y().disc_line_ids) {
                                            _.each(line.get_buy_x_get_dis_y().disc_line_ids, function (disc_line) {
                                                _.each(lines, function (orderline) {
                                                    // if (disc_line.product_id_dis && disc_line.product_id_dis[0] == orderline.product.id) {
                                                    if (disc_line.product_id_dis && disc_line.product_id_dis[0] && (jQuery.inArray(orderline.product.id, disc_line.product_id_dis) != -1)) {
                                                        var count = 0;
                                                        _.each(order.get_orderlines(), function (_line) {
                                                            if (_line.product.id == orderline.product.id) {
                                                                count += 1;
                                                            }
                                                        });
                                                        // if(count <= disc_line.qty){
                                                        var cart_line_qty = orderline.get_quantity();
                                                        if (cart_line_qty >= disc_line.qty) {
                                                            var prmot_disc_lines = [];
                                                            var flag = true;
                                                            order.get_orderlines().map(function (o_line) {
                                                                if (o_line.product.id == orderline.product.id) {
                                                                    if (o_line.get_is_rule_applied()) {
                                                                        flag = true;
                                                                    }
                                                                }
                                                            });
                                                            if (flag) {
                                                                // var extra_prod_qty = cart_line_qty - disc_line.qty;
                                                                // if (extra_prod_qty != 0) {
                                                                //     orderline.set_quantity(disc_line.qty);
                                                                // }
                                                                orderline.set_discount(disc_line.discount_dis_x);
                                                                orderline.set_buy_x_get_y_child_item({
                                                                    'rule_name': line.get_buy_x_get_dis_y().promotion.promotion_code,
                                                                    'promotion_type': line.get_buy_x_get_dis_y().promotion.promotion_type,
                                                                });
                                                                orderline.set_is_rule_applied(true);

                                                                // MCS
                                                                orderline.set_disc_type('multiply');
                                                                orderline.custom_promotion_id = promotion.id;
                                                                console.log('custom_promotion_id new 1')
                                                                console.log(promotion)
                                                                if (promotion.vendor_id && promotion.vendor_id[0]) {
                                                                    orderline.vendor_id = promotion.vendor_id[0];
                                                                }
                                                                orderline.vendor_shared = promotion.vendor_shared;
                                                                orderline.sarinah_shared = promotion.sarinah_shared;
                                                                // !MCS

                                                                self.pos.chrome.screens.products.order_widget.rerender_orderline(orderline);
                                                                // if (extra_prod_qty != 0) {
                                                                //     var new_line = new models.Orderline({}, { pos: self.pos, order: order, product: orderline.product });
                                                                //     new_line.set_quantity(extra_prod_qty);

                                                                //     // MCS
                                                                //     //                                                                new_line.custom_promotion_id = promotion.id;
                                                                //     // !MCS

                                                                //     order.add_orderline(new_line);
                                                                // }
                                                                return false;
                                                            }
                                                        }
                                                        //   }
                                                    }
                                                });
                                            });
                                        }
                                    }
                                    // start



                                    else if (promotion && promotion.promotion_type == "buy_x_get_cheapest_free") {
                                        if (!promotion.pos_condition_ids || promotion.pos_condition_ids.length === 0) return;

                                        _.each(promotion.pos_condition_ids, function (pos_condition_line_id) {
                                            var line_record = _.find(condition_list, obj => obj.id == pos_condition_line_id);
                                            if (!line_record || !line_record.product_x_id.includes(line.product.id)) return;
                                            var quantity_free = line_record.quantity_y;
                                            var discount_before_quantity = line_record.discount_before_quantity;
                                            var matching_orderlines = _.filter(order.get_orderlines(), obj => line_record.product_x_id.includes(obj.product.id));
                                            var total_qty = _.reduce(matching_orderlines, (sum, orderline) => sum + orderline.get_quantity(), 0);

                                            // Mengembalikan promo line yang dihapus
                                            _.each(_.filter(matching_orderlines, orderline => orderline.buy_x_get_cheapest_free && orderline.custom_promotion_id == promotion.id), function (promo_line) {
                                                var original_line = _.find(order.get_orderlines(), o => o.product.id === promo_line.product.id && !o.buy_x_get_cheapest_free);
                                                if (original_line) {
                                                    original_line.set_quantity(original_line.get_quantity() + promo_line.get_quantity());
                                                    order.remove_orderline(promo_line);
                                                } else {
                                                    if(line_record.apply_keep_before_discount==false){
                                                        promo_line.buy_x_get_cheapest_free = false;
                                                        promo_line.set_discount(0);
                                                        promo_line.set_is_rule_applied(false);
                                                        promo_line.custom_promotion_id = false;
                                                        promo_line.vendor_id = false;
                                                        promo_line.vendor_shared = false;
                                                        promo_line.sarinah_shared = false;
                                                    }
                                                }
                                            });


                                            if (total_qty >= line_record.quantity && line_record.quantity > 0) {
                                                var total_looping = (line_record.operator == "is_eql_to") ? 1 : Math.floor(total_qty / line_record.quantity);
                                                total_looping *= quantity_free || 1;
                                                for (var i = 1; i <= total_looping; i++) {
                                                    var filtered_orderlines = _.filter(matching_orderlines, orderline => !orderline.buy_x_get_cheapest_free || (orderline.buy_x_get_cheapest_free && orderline.discount === 0));
                                                    var cheapest_orderline = _.min(filtered_orderlines, orderline => orderline.get_unit_price());

                                                    if (!cheapest_orderline || cheapest_orderline === Infinity) {
                                                        console.log('Tidak ada orderline yang memenuhi syarat untuk Buy X Get Cheapest Free');
                                                        continue;
                                                    }

                                                    if (cheapest_orderline.get_quantity() > 1) {
                                                        cheapest_orderline.set_quantity(cheapest_orderline.get_quantity() - 1);

                                                        order.add_product(cheapest_orderline.get_product(), {
                                                            quantity: 1,
                                                            discount: 100,
                                                            merge: false,
                                                            buy_x_get_cheapest_free: true,
                                                            no_apply_promotion: true,
                                                        });

                                                        var new_orderline = order.get_last_orderline();
                                                        new_orderline.set_discount(100);
                                                        new_orderline.buy_x_get_cheapest_free = true;
                                                        new_orderline.set_quantity_discount({ 'rule_name': promotion.promotion_code });
                                                        new_orderline.set_is_rule_applied(true);

                                                        // MCS
                                                        new_orderline.custom_promotion_id = promotion?.id;
                                                        new_orderline.vendor_id = promotion?.vendor_id?.[0] ?? null; // Jika vendor_id kosong, set null
                                                        new_orderline.vendor_shared = promotion?.vendor_shared ?? false;
                                                        new_orderline.sarinah_shared = promotion?.sarinah_shared ?? false;
                                                        self.pos.chrome.screens.products.order_widget.rerender_orderline(new_orderline);
                                                    } else {
                                                        cheapest_orderline.set_discount(100);
                                                        cheapest_orderline.set_quantity_discount({ 'rule_name': promotion.promotion_code });
                                                        cheapest_orderline.buy_x_get_cheapest_free = true;
                                                        cheapest_orderline.set_is_rule_applied(true);

                                                        // MCS
                                                        cheapest_orderline.custom_promotion_id = promotion.id;
                                                        if (promotion.vendor_id && promotion.vendor_id[0]) {
                                                            cheapest_orderline.vendor_id = promotion.vendor_id[0];
                                                        }
                                                        cheapest_orderline.vendor_shared = promotion.vendor_shared;
                                                        cheapest_orderline.sarinah_shared = promotion.sarinah_shared;
                                                        self.pos.chrome.screens.products.order_widget.rerender_orderline(cheapest_orderline);
                                                    }
                                                }

                                            }
                                            else {

                                                if (!Array.isArray(matching_orderlines) || matching_orderlines.length === 0) return;

                                                for (let promo_line of matching_orderlines) {
                                                    if (!promo_line) continue;
                                                    if (discount_before_quantity > 0) {
                                                        promo_line.set_discount(discount_before_quantity);
                                                        promo_line.set_quantity_discount({ 'rule_name': promotion.promotion_code });
                                                        promo_line.buy_x_get_cheapest_free = true;
                                                        promo_line.set_is_rule_applied(true);

                                                        // MCS
                                                        promo_line.custom_promotion_id = promotion?.id;
                                                        promo_line.vendor_id = promotion?.vendor_id?.[0] ?? null; // Jika vendor_id kosong, set null
                                                        promo_line.vendor_shared = promotion?.vendor_shared ?? false;
                                                        promo_line.sarinah_shared = promotion?.sarinah_shared ?? false;



                                                    }
                                                }

                                                var last_orderline = order.get_last_orderline();
                                                if (last_orderline) {
                                                    self.pos.chrome.screens.products.order_widget.rerender_orderline(last_orderline);
                                                }
                                            }

                                            var matching_orderlines_new = _.filter(order.get_orderlines(), obj => line_record.product_x_id.includes(obj.product.id));

                                            var filtered_orderlines_free = _.filter(matching_orderlines_new, orderline =>
                                                orderline.buy_x_get_cheapest_free && orderline.discount === 100
                                            );

                                            var filtered_orderlines_not_free = _.filter(matching_orderlines_new, orderline =>
                                                (!orderline.buy_x_get_cheapest_free && !orderline.discount === 100) || (orderline.buy_x_get_cheapest_free && orderline.discount !== 100)
                                            );
                                            if (line_record.apply_keep_before_discount && discount_before_quantity > 0) {
                                                for (let promo_line of filtered_orderlines_not_free) {
                                                    if (!promo_line) continue;
                                                    if (discount_before_quantity > 0) {
                                                        promo_line.set_discount(discount_before_quantity);
                                                        promo_line.set_quantity_discount({ 'rule_name': promotion.promotion_code });
                                                        promo_line.buy_x_get_cheapest_free = true;
                                                        promo_line.set_is_rule_applied(true);

                                                        // MCS
                                                        promo_line.custom_promotion_id = promotion?.id;
                                                        promo_line.vendor_id = promotion?.vendor_id?.[0] ?? null; // Jika vendor_id kosong, set null
                                                        promo_line.vendor_shared = promotion?.vendor_shared ?? false;
                                                        promo_line.sarinah_shared = promotion?.sarinah_shared ?? false;



                                                    }
                                                }
                                            }

                                            if (filtered_orderlines_free.length > 1) {
                                                let productMap = new Map();

                                                // Kelompokkan berdasarkan product_id dan jumlahkan quantity
                                                for (let orderline of filtered_orderlines_free) {
                                                    let productId = orderline.product.id;

                                                    if (productMap.has(productId)) {
                                                        // Tambahkan quantity ke produk yang sudah ada
                                                        let existingOrderline = productMap.get(productId);
                                                        existingOrderline.set_quantity(existingOrderline.quantity + orderline.quantity);

                                                        // Tandai orderline lama untuk dihapus
                                                        order.remove_orderline(orderline);
                                                    } else {
                                                        // Simpan orderline pertama sebagai referensi
                                                        productMap.set(productId, orderline);
                                                    }
                                                }


                                            }
                                        });
                                    }








                                    // finish
                                    else if (promotion && promotion.promotion_type == "quantity_discount") {
                                        if (promotion.product_id_qty && promotion.product_id_qty[0]) {
                                            _.each(promotion.product_id_qty, function (product_id_qty_e) {
                                                var line_ids = [];
                                                if (product_id_qty_e == line.product.id) {
                                                    // line.set_has_aspl_promotion(true);
                                                    _.each(promotion.pos_quntity_ids, function (pos_quntity_id) {
                                                        var line_record = _.find(pos_get_qty_discount_list, function (obj) { return obj.id == pos_quntity_id });
                                                        if (line_record) {
                                                            if (line.get_quantity() >= line_record.quantity_dis) {
                                                                if (line_record.discount_dis) {
                                                                    line.set_discount(line_record.discount_dis);
                                                                    line.set_quantity_discount({
                                                                        'rule_name': promotion.promotion_code,
                                                                    });
                                                                    line.set_is_rule_applied(true);
                                                                    line.set_disc_type(promotion.type_disc_qty);

                                                                    // MCS
                                                                    line.custom_promotion_id = promotion.id;
                                                                    console.log('custom_promotion_id new 5')
                                                                    if (promotion.vendor_id && promotion.vendor_id[0]) {
                                                                        line.vendor_id = promotion.vendor_id[0];
                                                                    }
                                                                    line.vendor_shared = promotion.vendor_shared;
                                                                    line.sarinah_shared = promotion.sarinah_shared;
                                                                    // !MCS

                                                                    self.pos.chrome.screens.products.order_widget.rerender_orderline(line);
                                                                    //                                                            return false;
                                                                }
                                                            }
                                                        }
                                                    });
                                                }
                                            });
                                        }
                                    }
                                    // this is for one product but have multiple discount like if you buy 2 discount is 2 dollar and if you buy 3 discount is 3 dollar
                                    else if (promotion && promotion.promotion_type == "quantity_price") {
                                        if (promotion.product_id_amt && promotion.product_id_amt[0] == line.product.id) {
                                            var line_ids = [];
                                            _.each(promotion.pos_quntity_amt_ids, function (pos_quntity_amt_id) {
                                                var line_record = _.find(pos_qty_discount_amt, function (obj) { return obj.id == pos_quntity_amt_id });
                                                if (line_record) {
                                                    if (line.get_quantity() >= line_record.quantity_amt) {
                                                        if (line_record.discount_price) {
                                                            line.set_discount_amt(line_record.discount_price);
                                                            line.set_discount_amt_rule(promotion.promotion_code);
                                                            var prod_price = line.product.get_price(order.pricelist, 1)
                                                            console.log(prod_price)
                                                            line.set_unit_price(((prod_price * line.get_quantity()) - line_record.discount_price) / line.get_quantity());
                                                            //													line.set_unit_price(((line.get_unit_price()*line.get_quantity()) - line_record.discount_price)/line.get_quantity());
                                                            //                                                    line.set_unit_price(line_record.discount_price);
                                                            line.set_is_rule_applied(true);

                                                            // MCS TODO CHECK FIX PRICE
                                                            //                                                    line.set_fix_discount(line_record.discount_price);
                                                            line.set_disc_type('multiply');
                                                            line.custom_promotion_id = promotion.id;
                                                            console.log('custom_promotion_id new 6')
                                                            if (promotion.vendor_id && promotion.vendor_id[0]) {
                                                                line.vendor_id = promotion.vendor_id[0];
                                                            }
                                                            line.vendor_shared = promotion.vendor_shared;
                                                            line.sarinah_shared = promotion.sarinah_shared;
                                                            // line.set_fix_discount(line_record.discount_price);
                                                            // !MCS

                                                            self.pos.chrome.screens.products.order_widget.rerender_orderline(line);
                                                            return false;
                                                        }
                                                    }
                                                }
                                            });
                                        }
                                    }
                                    else if (promotion && promotion.promotion_type == "quantity_price_all") {
                                        // loop product_amt_multi_ids
                                        for(var i = 0; i < promotion.product_amt_multi_ids.length; i++){
                                            if (promotion.product_amt_multi_ids[i] == line.product.id) {
                                                var line_ids = [];
                                                _.each(promotion.pos_quntity_amt_ids, function (pos_quntity_amt_id) {
                                                    var line_record = _.find(pos_qty_discount_amt, function (obj) { return obj.id == pos_quntity_amt_id });
                                                    if (line_record) {
                                                        if (line.get_quantity() >= line_record.quantity_amt) {
                                                            if (line_record.discount_price) {
                                                                line.set_discount_amt(line_record.discount_price);
                                                                line.set_discount_amt_rule(promotion.promotion_code);
                                                                var prod_price = line.product.get_price(order.pricelist, 1);
                                                                console.log(prod_price);
                                                                line.set_unit_price(((prod_price * line.get_quantity()) - line_record.discount_price) / line.get_quantity());
                                                                line.set_is_rule_applied(true);
                            
                                                                // MCS TODO CHECK FIX PRICE
                                                                line.set_disc_type('multiply');
                                                                line.custom_promotion_id = promotion.id;
                                                                console.log('custom_promotion_id new 6');
                                                                if (promotion.vendor_id && promotion.vendor_id[0]) {
                                                                    line.vendor_id = promotion.vendor_id[0];
                                                                }
                                                                line.vendor_shared = promotion.vendor_shared;
                                                                line.sarinah_shared = promotion.sarinah_shared;
                                                                // !MCS
                            
                                                                self.pos.chrome.screens.products.order_widget.rerender_orderline(line);
                                                                return false;
                                                            }
                                                        }
                                                    }
                                                });
                                            }
                                        }
                                    }

                                    else if (promotion && promotion.promotion_type == "discount_on_multi_product") {
                                        if (promotion.multi_products_discount_ids && promotion.multi_products_discount_ids[0]) {
                                            _.each(promotion.multi_products_discount_ids, function (disc_line_id) {
                                                var disc_line_record = _.find(pos_discount_multi_prods, function (obj) { return obj.id == disc_line_id });
                                                if (disc_line_record) {
                                                    self.check_products_for_disc(disc_line_record, promotion);
                                                }
                                            })
                                        }
                                    }
                                    else if (promotion && promotion.promotion_type == "discount_on_multi_categ") {
                                        if (promotion.multi_categ_discount_ids && promotion.multi_categ_discount_ids[0]) {
                                            _.each(promotion.multi_categ_discount_ids, function (disc_line_id) {
                                                var disc_line_record = _.find(pos_discount_multi_categ, function (obj) { return obj.id == disc_line_id });
                                                if (disc_line_record) {
                                                    //                                            console.log("Masuk Sini");
                                                    self.check_categ_for_disc(disc_line_record, promotion);
                                                }
                                            })
                                        }
                                    }
                                    // MCS Seasonal
                                    else if (promotion && promotion.promotion_type == "discount_on_product") {
                                        if (promotion.discount_seasonal_ids && promotion.discount_seasonal_ids[0]) {
                                            _.each(promotion.discount_seasonal_ids, function (disc_line_id) {
                                                var disc_line_record = _.find(pos_discount_seasonal, function (obj) { return obj.id == disc_line_id });
                                                if (disc_line_record) {
                                                    // console.log(disc_line_record);
                                                    if (jQuery.inArray(line.product.id, disc_line_record.product_ids) != -1) {
                                                        line.set_discount(disc_line_record.products_discount);
                                                        var discount_type = '';
                                                        if (disc_line_record.discount_type == 'on_top') {
                                                            discount_type = '' + disc_line_record.products_discount_1 + '% + ' + disc_line_record.products_discount_2 + '%'
                                                        }

                                                        line.set_quantity_discount({
                                                            'rule_name': promotion.promotion_code,
                                                            'discount_type': discount_type
                                                        });

                                                        line.set_is_rule_applied(true);
                                                        line.set_disc_type('multiply');


                                                        line.custom_promotion_id = promotion.id;
                                                        console.log('custom_promotion_id new 7')
                                                        if (promotion.vendor_id && promotion.vendor_id[0]) {
                                                            line.vendor_id = promotion.vendor_id[0];
                                                        }
                                                        line.vendor_shared = promotion.vendor_shared;
                                                        line.sarinah_shared = promotion.sarinah_shared;

                                                        // for re render
                                                        self.pos.chrome.screens.products.order_widget.rerender_orderline(line);
                                                    }
                                                }
                                            })
                                        }
                                    }
                                    // MCS promotional Customer
                                    else if (promotion && promotion.promotion_type == "discount_on_customer") {
                                        if (client && client.member_type) {
                                            var get_discount = false;
                                            console.log(line.get_is_rule_applied())
                                            if (!line.get_is_rule_applied()) {
                                                get_discount = true;
                                            }
                                            else if (line.custom_promotion_id && line.custom_promotion_id == promotion.id) {
                                                get_discount = true;
                                            }

                                            if (line.price <= 0) {
                                                get_discount = false;
                                            }
                                            if (get_discount) {
                                                var discount = 0;
                                                if (client.member_type == 'regular') {
                                                    if (promotion.percent_discount_reg > 0) {
                                                        discount = promotion.percent_discount_reg;
                                                    }
                                                }
                                                else if (client.member_type == 'vip') {
                                                    if (promotion.percent_discount_vip > 0) {
                                                        discount = promotion.percent_discount_vip;
                                                    }
                                                }
                                                else if (client.member_type == 'employee') {
                                                    if (promotion.percent_discount_emp > 0) {
                                                        discount = promotion.percent_discount_emp;
                                                    }
                                                }
                                                else if (client.member_type == 'tourist') {
                                                    if (promotion.percent_discount_tour > 0) {
                                                        discount = promotion.percent_discount_tour;
                                                    }
                                                }

                                                line.set_discount(discount);
                                                line.set_quantity_discount({
                                                    'rule_name': promotion.promotion_code
                                                });

                                                line.set_is_rule_applied(true);
                                                line.set_disc_type('multiply');
                                                line.custom_promotion_id = promotion.id;
                                                console.log('custom_promotion_id new 8')
                                                if (promotion.vendor_id && promotion.vendor_id[0]) {
                                                    line.vendor_id = promotion.vendor_id[0];
                                                }
                                                line.vendor_shared = promotion.vendor_shared;
                                                line.sarinah_shared = promotion.sarinah_shared;
                                                // for re render
                                                self.pos.chrome.screens.products.order_widget.rerender_orderline(line);
                                            }
                                        }
                                    }
                                    // !MCS
                                    //                            else if(promotion && promotion.promotion_type == "discount_on_above_price"){
                                    //                                if(promotion && promotion.discount_price_ids && promotion.discount_price_ids[0]){
                                    //                                    _.each(promotion.discount_price_ids, function(line_id){
                                    //                                        var line_record = _.find(pos_discount_above_price, function(obj) { return obj.id == line_id});
                                    //                                        if(line_record && line_record.product_brand_ids && line_record.product_brand_ids[0]
                                    //                                            && line_record.product_categ_ids && line_record.product_categ_ids[0]){
                                    //                                            if(line.product.product_brand_id && line.product.product_brand_id[0]){
                                    //                                                if($.inArray(line.product.product_brand_id[0], line_record.product_brand_ids) != -1){
                                    //                                                    if(line.product.pos_categ_id){
                                    //                                                        var product_category = self.pos.db.get_category_by_id(line.product.pos_categ_id[0])
                                    //                                                        if(product_category){
                                    //                                                            if($.inArray(product_category.id, line_record.product_categ_ids) != -1){
                                    //                                                                if(line_record.discount_type == "fix_price"){
                                    //                                                                    if(line.product.lst_price >= line_record.price && line.quantity > 0){
                                    //                                                                        if(line_record.price){
                                    //                                                                            line.set_discount_amt(line_record.price);
                                    //                                                                            line.set_discount_amt_rule(line_record.pos_promotion_id[1]);
                                    //                                                                            line.set_unit_price(((line.get_unit_price()*line.get_quantity()) - line_record.price)/line.get_quantity());
                                    //                                                                            line.set_is_rule_applied(true);
                                    //                                                                            self.pos.chrome.screens.products.order_widget.rerender_orderline(line);
                                    //                                                                        }
                                    //                                                                    }
                                    //                                                                } else if(line_record.discount_type == "percentage"){
                                    //                                                                    if(line_record.discount){
                                    //                                                                        if(line.product.lst_price >= line_record.price && line.quantity > 0){
                                    //                                                                            line.set_discount(line_record.discount);
                                    //                                                                            line.set_is_rule_applied(true);
                                    //                                                                        }
                                    //                                                                    }
                                    //                                                                } else if(line_record.discount_type == "free_product"){
                                    //                                                                    if(line_record.free_product && line_record.free_product[0]){
                                    //                                                                        var product = self.pos.db.get_product_by_id(line_record.free_product[0]);
                                    //                                                                        var new_line = new models.Orderline({}, {pos: self.pos, order: order, product: product});
                                    //                                                                        new_line.set_quantity(1);
                                    //                                                                        new_line.set_unit_price(0);
                                    //                                                                        new_line.set_promotion({
                                    //                                                                            'prom_prod_id':line_record.free_product[0],
                                    //                                                                            'parent_product_id':line.id,
                                    //                                                                            'rule_name':line_record.pos_promotion_id[1],
                                    //                                                                        });
                                    //                                                                        new_line.set_is_rule_applied(true);
                                    //                                                                        order.add_orderline(new_line);
                                    //                                                                        line.set_child_line_id(new_line.id);
                                    //                                                                        line.set_is_rule_applied(true);
                                    //                                                                    }
                                    //                                                                }
                                    //                                                            }
                                    //                                                        }
                                    //                                                    }
                                    //                                                }
                                    //                                            }
                                    //                                        }else if(line_record.product_brand_ids.length <= 0 && line_record.product_categ_ids.length > 0){
                                    //                                            if(line.product.pos_categ_id){
                                    //                                                var product_category = self.pos.db.get_category_by_id(line.product.pos_categ_id[0]);
                                    //                                                if(product_category){
                                    //                                                    if($.inArray(product_category.id, line_record.product_categ_ids) != -1){
                                    //                                                        if(line_record.discount_type == "fix_price"){
                                    //                                                            if(line.product.lst_price >= line_record.price && line.quantity > 0){
                                    //                                                                if(line_record.price){
                                    //                                                                    line.set_discount_amt(line_record.price);
                                    //                                                                    line.set_discount_amt_rule(line_record.pos_promotion_id[1]);
                                    //                                                                    line.set_unit_price(((line.get_unit_price()*line.get_quantity()) - line_record.price)/line.get_quantity());
                                    //                                                                    line.set_is_rule_applied(true);
                                    //                                                                    self.pos.chrome.screens.products.order_widget.rerender_orderline(line);
                                    //                                                                }
                                    //                                                            }
                                    //                                                        } else if(line_record.discount_type == "percentage"){
                                    //                                                            if(line_record.discount){
                                    //                                                                if(line.product.lst_price >= line_record.price && line.quantity > 0){
                                    //                                                                    line.set_discount(line_record.discount);
                                    //                                                                    line.set_is_rule_applied(true);
                                    //                                                                }
                                    //                                                            }
                                    //                                                        } else if(line_record.discount_type == "free_product"){
                                    //                                                            if(line_record.free_product && line_record.free_product[0]){
                                    //                                                                var product = self.pos.db.get_product_by_id(line_record.free_product[0]);
                                    //                                                                var new_line = new models.Orderline({}, {pos: self.pos, order: order, product: product});
                                    //                                                                new_line.set_quantity(1);
                                    //                                                                new_line.set_unit_price(0);
                                    //                                                                new_line.set_promotion({
                                    //                                                                    'prom_prod_id':line_record.free_product[0],
                                    //                                                                    'parent_product_id':line.id,
                                    //                                                                    'rule_name':line_record.pos_promotion_id[1],
                                    //                                                                });
                                    //                                                                new_line.set_is_rule_applied(true);
                                    //                                                                order.add_orderline(new_line);
                                    //                                                                line.set_child_line_id(new_line.id);
                                    //                                                                line.set_is_rule_applied(true);
                                    //                                                            }
                                    //                                                        }
                                    //                                                    }
                                    //                                                }
                                    //                                            }
                                    //                                        }else if(line_record.product_categ_ids.length == 0 && line_record.product_brand_ids.length > 0){
                                    //                                            if(line.product.product_brand_id && line.product.product_brand_id[0]){
                                    //                                                if($.inArray(line.product.product_brand_id[0], line_record.product_brand_ids) != -1){
                                    //                                                    if(line_record.discount_type == "fix_price"){
                                    //                                                        if(line.product.lst_price >= line_record.price && line.quantity > 0){
                                    //                                                            if(line_record.price){
                                    //                                                                line.set_discount_amt(line_record.price);
                                    //                                                                line.set_discount_amt_rule(line_record.pos_promotion_id[1]);
                                    //                                                                line.set_unit_price(((line.get_unit_price()*line.get_quantity()) - line_record.price)/line.get_quantity());
                                    //                                                                line.set_is_rule_applied(true);
                                    //                                                                self.pos.chrome.screens.products.order_widget.rerender_orderline(line);
                                    //                                                            }
                                    //                                                        }
                                    //                                                    } else if(line_record.discount_type == "percentage"){
                                    //                                                        if(line_record.discount){
                                    //                                                            if(line.product.lst_price >= line_record.price && line.quantity > 0){
                                    //                                                                line.set_discount(line_record.discount);
                                    //                                                                line.set_is_rule_applied(true);
                                    //                                                            }
                                    //                                                        }
                                    //                                                    } else if(line_record.discount_type == "free_product"){
                                    //                                                        if(line_record.free_product && line_record.free_product[0]){
                                    //                                                            var product = self.pos.db.get_product_by_id(line_record.free_product[0]);
                                    //                                                            var new_line = new models.Orderline({}, {pos: self.pos, order: order, product: product});
                                    //                                                            new_line.set_quantity(1);
                                    //                                                            new_line.set_unit_price(0);
                                    //                                                            new_line.set_promotion({
                                    //                                                                'prom_prod_id':line_record.free_product[0],
                                    //                                                                'parent_product_id':line.id,
                                    //                                                                'rule_name':line_record.pos_promotion_id[1],
                                    //                                                            });
                                    //                                                            new_line.set_is_rule_applied(true);
                                    //                                                            order.add_orderline(new_line);
                                    //                                                            line.set_child_line_id(new_line.id);
                                    //                                                            line.set_is_rule_applied(true);
                                    //                                                        }
                                    //                                                    }
                                    //                                                }
                                    //                                            }
                                    //                                        }
                                    //                                    });
                                    //                                }
                                    //                            }
                                }
                            });
                        }
                        if (line.is_free_product_new_line) {
                            line.order.remove_orderline(line);
                        }
                    });
                }
            }
        },
        check_categ_for_disc: function (disc_line, promotion) {
            var self = this;
            var order = self.pos.get_order();
            var lines = self.get_new_order_lines();
            var categ_ids = disc_line.categ_ids;
            var discount = disc_line.categ_discount;
            if (categ_ids && categ_ids[0] && discount) {
                _.each(categ_ids, function (categ_id) {
                    _.each(lines, function (line) {
                        var list = [];
                        var has_parent = true;
                        var prod_categ = line.product.categ;
                        list.push(prod_categ.id);
                        while (has_parent) {
                            if (prod_categ.parent) {
                                list.push(prod_categ.parent.id);
                                prod_categ = prod_categ.parent;
                            }
                            else {
                                has_parent = false;
                            }
                        }
                        if ($.inArray(categ_id, list) != -1) {
                            var apply = true;
                            if (promotion.vendor_id && promotion.vendor_id[0]) {
                                if (line.product.owner_id && line.product.owner_id[0]) {
                                    if (line.product.owner_id[0] != promotion.vendor_id[0]) {
                                        apply = false;
                                    }
                                }
                            }
                            if (apply) {
                                line.set_discount(discount);
                                line.set_is_rule_applied(true);
                                line.set_multi_prod_categ_rule(promotion.promotion_code);
                                self.pos.chrome.screens.products.order_widget.rerender_orderline(line);
                            }
                        }
                    });
                });
            }
        },
        // set_client: function(client){
        //     var self = this;
        //     _super_Order.set_client.apply(this, arguments);
        //     console.log(self.get_order())
        // },
        calculate_discount_amt: function () {
            var self = this;
            var order = self.pos.get_order();
            var client = order.get_client();
            var total = order ? order.get_total_with_tax() : 0;

            if (order.get_orderlines()) {
                _.each(order.get_orderlines(), function (linee) {
                    if (linee.get_price_with_tax() < 0) {
                        total = total - linee.get_price_with_tax()
                    }
                })
            }

            var promotion_list = self.pos.pos_promotions;
            var discount = 0;
            var current_time = Number(moment(new Date().getTime()).locale('en').format("H"));
            if (promotion_list && promotion_list[0]) {
                _.each(promotion_list, function (promotion) {
                    if ((Number(promotion.from_time) <= current_time && Number(promotion.to_time) > current_time) || (!promotion.from_time && !promotion.to_time)) {
                        if (promotion.promotion_type == 'dicount_total') {
                            if (promotion.operator == 'greater_than_or_eql') {
                                if (promotion.total_amount && total >= promotion.total_amount) {
                                    if (promotion.discount_product && promotion.discount_product[0]) {
                                        discount = (total * promotion.total_discount) / 100;
                                        if (client && client.member_type) {
                                            if (client.member_type == 'vip') {
                                                if (promotion.total_discount_vip > 0) {
                                                    discount = (total * promotion.total_discount_vip) / 100;
                                                }
                                            }
                                            if (client.member_type == 'employee') {
                                                if (promotion.total_discount_emp > 0) {
                                                    discount = (total * promotion.total_discount_emp) / 100;
                                                }
                                            }
                                            if (client.member_type == 'tourist') {
                                                if (promotion.total_discount_emp > 0) {
                                                    discount = (total * promotion.total_discount_tour) / 100;
                                                }
                                            }
                                        }
                                        order.set_discount_product_id(promotion.discount_product[0]);
                                        //                                        order.set_discount_history(true);
                                    }
                                }
                            } else if (promotion.operator == 'is_eql_to') {
                                if (promotion.total_amount && total == promotion.total_amount) {
                                    if (promotion.discount_product && promotion.discount_product[0]) {
                                        discount = (total * promotion.total_discount) / 100;
                                        if (client && client.member_type) {
                                            if (client.member_type == 'vip') {
                                                if (promotion.total_discount_vip > 0) {
                                                    discount = (total * promotion.total_discount_vip) / 100;
                                                }
                                            }
                                            if (client.member_type == 'emp') {
                                                if (promotion.total_discount_emp > 0) {
                                                    discount = (total * promotion.total_discount_emp) / 100;
                                                }
                                            }
                                            if (client.member_type == 'tourist') {
                                                if (promotion.total_discount_emp > 0) {
                                                    discount = (total * promotion.total_discount_tour) / 100;
                                                }
                                            }
                                        }
                                        order.set_discount_product_id(promotion.discount_product[0]);
                                        //                                        order.set_discount_history(true);
                                    }
                                }
                            }
                        }
                    }
                });
            }
            return Number(discount);
        },
    });

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            this.custom_promotion_id = null;
            this.free_product_y_id = null;
            this.free_product_x_id = null;
            this.is_free_product_new_line = false;
            this.vendor_id = null;
            this.vendor_shared = null;
            this.sarinah_shared = null;
            this.fix_discount = 0;
            this.has_aspl_promotion = false;
            this.disc_type = false;
            _super_orderline.initialize.call(this, attr, options);
        },
        can_be_merged_with: function (orderline) {
            var result = _super_orderline.can_be_merged_with.call(this, orderline);
            console.log(result)
            if (!result) {
                if (!this.manual_price) {
                    if (this.get_promotion() && this.get_promotion().parent_product_id) {
                        return false;
                    }
                    else if (this.get_is_rule_applied()) {
                        if (this.get_product().id === orderline.get_product().id) {
                            if (this.get_disc_type()) {
                                if (this.get_disc_type() == 'multiply') {
                                    return true;
                                }
                                else {
                                    return false;
                                }
                            }
                            else {
                                return false;
                            }
                        }
                        else {
                            return false;
                        }
                    }
                    else {
                        return (this.get_product().id === orderline.get_product().id);
                    }
                }
                else {
                    return false;
                }
            }
            return true;
        },
        set_disc_type: function (disc_type) {
            this.disc_type = disc_type;
        },
        get_disc_type: function () {
            return this.disc_type;
        },
        export_for_printing: function () {
            var dict = _super_orderline.export_for_printing.call(this);
            var new_attr = {
                custom_promotion_id: this.custom_promotion_id,
                free_product_y_id: this.free_product_y_id,
                free_product_x_id: this.free_product_x_id,
                is_free_product_new_line: this.is_free_product_new_line,
                vendor_id: this.vendor_id,
                vendor_shared: this.vendor_shared,
                sarinah_shared: this.sarinah_shared,
                fix_discount: this.fix_discount,
            }
            $.extend(dict, new_attr);
            return dict;
        },
        get_has_aspl_promotion: function () {
            var self = this;
            var line = self.product.id;
            var promotion_list = self.pos.pos_promotions;
            var condition_list = self.pos.pos_conditions;
            var current_time = Number(moment(new Date().getTime()).locale('en').format("H"));
            // Todo check promo lainnya
            if (promotion_list && promotion_list[0]) {
                _.each(promotion_list, function (promotion) {
                    if ((Number(promotion.from_time) <= current_time && Number(promotion.to_time) > current_time) || (!promotion.from_time && !promotion.to_time)) {
                        if (promotion && promotion.promotion_type == "buy_x_get_y") {
                            if (promotion.pos_condition_ids && promotion.pos_condition_ids[0]) {
                                _.each(promotion.pos_condition_ids, function (pos_condition_line_id) {
                                    var line_record = _.find(condition_list, function (obj) { return obj.id == pos_condition_line_id });
                                    if (line_record) {
                                        if (line_record.product_x_id && line_record.product_x_id[0] == line.product.id) {
                                            return true
                                        }
                                    }
                                });
                            }
                        }
                    }
                });
            }

            return self.has_aspl_promotion;
        },
        get_custom_promotion_id: function () {
            var self = this;
            return self.custom_promotion_id;
        },
        get_free_product_y_id: function () {
            var self = this;
            return self.free_product_y_id;
        },
        get_free_product_x_id: function () {
            var self = this;
            return self.free_product_x_id;
        },
        get_vendor_id: function () {
            var self = this;
            return self.vendor_id;
        },
        get_vendor_shared: function () {
            var self = this;
            return self.vendor_shared;
        },
        get_sarinah_shared: function () {
            var self = this;
            return self.sarinah_shared;
        },
        get_fix_discount: function () {
            var self = this;
            return self.fix_discount;
        },
        //        set_fix_discount: function(discount){
        //            this.fix_discount = discount;
        //        },
        export_as_JSON: function () {
            var self = this;
            var loaded = _super_orderline.export_as_JSON.call(this);
            loaded.custom_promotion_id = self.get_custom_promotion_id();
            console.log('custom_promotion_id new 10')
            loaded.free_product_y_id = self.get_free_product_y_id();
            loaded.free_product_x_id = self.get_free_product_x_id();
            loaded.is_free_product_new_line = self.is_free_product_new_line;
            loaded.vendor_id = self.get_vendor_id();
            loaded.vendor_shared = self.get_vendor_shared();
            loaded.sarinah_shared = self.get_sarinah_shared();
            loaded.fix_discount = self.get_fix_discount();
            return loaded;
        },
        init_from_JSON: function (json) {
            var self = this;
            var loaded = _super_orderline.init_from_JSON.call(this, json);
            this.custom_promotion_id = json.custom_promotion_id;
            console.log('custom_promotion_id new 9')
            this.free_product_y_id = json.free_product_y_id;
            this.free_product_x_id = json.free_product_x_id;
            this.is_free_product_new_line = json.is_free_product_new_line;
            this.vendor_id = json.vendor_id;
            this.vendor_shared = json.vendor_shared;
            this.sarinah_shared = json.sarinah_shared;
            this.fix_discount = json.fix_discount;
        },
    });

    var PosDiscountBxgyfButton = screens.ActionButtonWidget.extend({
        template: 'PosDiscountBxgyfButton',

        print_xml: function () {
            rpc.query({
                model: 'report.point_of_sale.report_saledetails',
                method: 'get_pos_sale_details',
                args: [false, false, self.pos.config.id],
            }).then(function (result) {
                var env = {
                    company: self.pos.company,
                    pos: self.pos,
                    categs: result.categs,
                    payments: result.payments,
                    taxes: result.taxes,
                    total_paid: result.total_paid,
                    date: (new Date()).toLocaleString(),
                    pos_name: result.pos_name,
                    cashier_name: result.cashier_name,
                    session_start: result.session_start,
                    session_end: result.session_end,
                    sales_amount: result.sales_amount,
                    return_amount: result.return_amount,
                    opening_balance: result.opening_balance,
                    total_with_tax: result.total_with_tax,
                    total_without_tax: result.total_without_tax,
                    total_tax: result.total_tax,
                    total_discount: result.total_discount,
                    widget: self,
                };
                var report = QWeb.render('WvSaleDetailsReport', env);
                self.pos.proxy.print_receipt(report);
            });
        },
        button_click: function () {
            self = this;

            var order = self.pos.get_order();

            var serialized = order.export_as_JSON();
            rpc.query({
                model: 'pos.promotion',
                method: 'get_buy_x_get_y',
                args: [serialized],
            }).then(function (result) {
                let data_json = JSON.parse(result)

                self.pos.gui.show_popup('customer_free_product', {
                    'promotion_line_id': data_json.promotion_line_id,
                    'list_final': data_json.list_final
                });
            });
        },
    });

    screens.ClientListScreenWidget.include({
        save_changes: function () {
            var self = this;
            self._super();
            var order = this.pos.get_order();
            var change_value = true;
            if (order.is_bxgy) {
                change_value = false
            }
            order.apply_promotion(change_value);
        },
    });
    screens.define_action_button({
        'name': 'Buy x Get y Free',
        'widget': PosDiscountBxgyfButton,
    });

});