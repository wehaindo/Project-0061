odoo.define('mcs_aspl_pos_promotion.popup_free', function (require) {
    "use strict";

    var popup_widget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var QWeb = core.qweb;
    var models = require('point_of_sale.models');

    var FreeProductPopup = popup_widget.extend({
        template: 'FreeProductPopup',
        show: function (options) {
            var self = this;
            this._super(options);

            self.render_list();
            $('.free_product-list tr').eq(1).addClass('selected');

            $(".product_free").on("click", function (e) {
                $("#discount_error").hide();
                $(".product_free").removeClass('selected');
                $(this).addClass('selected');;
            });

            $(".button.apply").on('click', function () {
                var order = self.pos.get_order();
                var lines = order.get_orderlines();
                var list_final = self.options.list_final;
                var promotion_line_id = self.options.promotion_line_id;

                /* Commented By Yayat 
                _.each(lines, function (line) {

                    _.each(promotion_line_id, function (promotion_line) {
                        if (line.free_product_x_id && line.free_product_x_id == promotion_line) {
                            line.set_discount(0);
                            line.set_quantity_discount({});
                            line.set_is_rule_applied(false);
                            line.set_disc_type(false);
                            line.custom_promotion_id = null;
                            line.vendor_id = null;
                            line.vendor_shared = null;
                            line.sarinah_shared = null;
                        }
                    });

                    _.each(list_final, function (final) {
                        if (line.product.id == final.product_id) {
                            if (final.new_qty == final.free_qty){
                                line.set_quantity(final.free_qty)
                                line.set_discount(100);

                                line.custom_promotion_id = final.promotional_id;
                                line.vendor_id = final.vendor_id;

                                line.vendor_shared = final.vendor_shared;
                                line.sarinah_shared = final.sarinah_shared;

                                line.set_quantity_discount({
                                    'rule_name': final.promotion_code
                                });

                                line.set_is_rule_applied(true);
                            }
                            else{
                                line.set_discount(0);
                                line.set_quantity(final.new_qty);
                                line.set_quantity_discount({});
                                line.set_is_rule_applied(false);
                                line.set_disc_type(false);
                                line.custom_promotion_id = null;
                                line.vendor_id = null;
                            }
                        }
                    });
                });
                _.each(list_final, function (final) {
                    if (final.is_new_line) {
                        var product = self.pos.db.get_product_by_id(final.product_id);
                        var new_line = new models.Orderline({}, { pos: self.pos, order: order, product: product });
                        new_line.set_quantity(final.free_qty)
                        new_line.set_discount(100);
                        new_line.set_is_rule_applied(true);

                        new_line.custom_promotion_id = final.promotional_id;
                        new_line.vendor_id = final.vendor_id;

                        new_line.vendor_shared = final.vendor_shared;
                        new_line.sarinah_shared = final.sarinah_shared;

                        new_line.free_product_y_id = final.free_product_y_id;
                        new_line.free_product_x_id = final.free_product_x_id;
                        new_line.is_free_product_new_line = true;

                        new_line.set_quantity_discount({
                            'rule_name': final.promotion_code
                        });
                        order.add_orderline(new_line);
                    }
                });
                if (list_final){
                    order.is_bxgy = true;
                    order.list_ori_bxgy = list_final
                }
		End Commented By Yayat */
		
		/* Ganti By Yayat */
		var product = self.pos.db.get_product_by_id(list_final[0].product_id);
                var new_line = new models.Orderline({}, { pos: self.pos, order: order, product: product });
                new_line.set_quantity(list_final[0].free_qty)
                new_line.set_discount(100);
                new_line.set_is_rule_applied(true);

                new_line.custom_promotion_id = list_final[0].promotional_id;
                new_line.vendor_id = list_final[0].vendor_id;

                new_line.vendor_shared = list_final[0].vendor_shared;
                new_line.sarinah_shared = list_final[0].sarinah_shared;

                new_line.free_product_y_id = list_final[0].free_product_y_id;
                new_line.free_product_x_id = list_final[0].free_product_x_id;
                new_line.is_free_product_new_line = true;

                new_line.set_quantity_discount({
                    'rule_name': list_final[0].promotion_code
                });
                order.add_orderline(new_line);
		/* End Ganti By Yayat */
                self.gui.close_popup();
                self.gui.current_screen.order_widget.numpad_state.reset();

            });

            /*remove_disc*/
            $(".button.cancel").on('click', function () {
                self.gui.close_popup();
                self.gui.current_screen.order_widget.numpad_state.reset();
            });
        },
        render_list: function () {
            var contents = this.$el[0].querySelector('.free_product-list-contents');

            contents.innerHTML = "";

            if (this.options.list_final && this.options.list_final[0]) {
                var list_final = this.options.list_final;
                for (var i = 0; i < list_final.length; i++) {
                    //                var discount = discounts[i];

                    var product = this.pos.db.get_product_by_id(list_final[i].product_id);
                    var qty = list_final[i].free_qty


                    var discountline_html = QWeb.render('ProductFreeLine', { widget: this, free_product: { 'display_name': product.display_name, 'qty': qty } });
                    var discountline = document.createElement('tbody');
                    discountline.innerHTML = discountline_html;
                    discountline = discountline.childNodes[1];
                    contents.appendChild(discountline);
                }
            }
        },
        //        renderElement: function(){
        //            var self = this;
        //            self._super();
        //            var discount_id = parseInt($('.product_discount.selected').attr('id'));
        //        },
    });

    gui.define_popup({ name: 'customer_free_product', widget: FreeProductPopup });

});
