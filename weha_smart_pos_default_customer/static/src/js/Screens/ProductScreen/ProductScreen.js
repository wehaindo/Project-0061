odoo.define("weha_smart_pos_default_customer.ProductScreen", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");

    const DefaultCustomerProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
                var self = this;
                var order = self.env.pos.get_order();
                if (!order.get_partner()) {
                    if (self.env.pos.config.is_set_default_customer && self.env.pos.config.customer_id) {
                        var customer_id = self.env.pos.db.get_partner_by_id(self.env.pos.config.customer_id[0]);
                        if (customer_id) {
                            order.set_partner(customer_id);
                        }
                    } else if (self.env.pos && self.env.pos.get_order()) {
                        self.env.pos.get_order().set_partner(null);
                    }
                }
            }
        };

    Registries.Component.extend(ProductScreen, DefaultCustomerProductScreen);
});
