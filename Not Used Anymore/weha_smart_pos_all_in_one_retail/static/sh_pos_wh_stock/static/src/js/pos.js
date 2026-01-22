odoo.define("sh_pos_wh_stock.ProductQtyPopup", function (require) {
    "use strict";

    const { useState, useSubEnv } = owl.hooks;
    const PosComponent = require("point_of_sale.PosComponent");
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const Registries = require("point_of_sale.Registries");
    var DB = require("point_of_sale.DB");
    var utils = require("web.utils");
    var round_pr = utils.round_precision;
    var field_utils = require("web.field_utils");
    var models = require("point_of_sale.models");
    const { Gui } = require("point_of_sale.Gui");
    models.load_fields("product.product", ["qty_available", "image_1920", "type"]);

    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        get_image_url: function (product_id) {
            return window.location.origin + "/web/image?model=product.product&field=image_1920&id=" + product_id;
        },
        set_quantity: function (quantity, keep_price) {
            this.order.assert_editable();
            var quant_by_product_id = this.pos.db.quant_by_product_id[this.product.id];
            var qty_available = quant_by_product_id ? quant_by_product_id[this.pos.config.sh_pos_location[0]] : 0;
            if (quantity === "remove") {
                this.order.remove_orderline(this);
                return;
            } else {
                var quant = field_utils.parse.float("" + quantity) || 0;
                var unit = this.get_unit();
                if (unit) {
                    if (unit.rounding) {
                        var decimals = this.pos.dp["Product Unit of Measure"];
                        var rounding = Math.max(unit.rounding, Math.pow(10, -decimals));

                        if (round_pr(quant, rounding) && this.pos.config.sh_show_qty_location && this.product.type == "product" && !this.product["is_added"]) {
                            if (qty_available - round_pr(quant, rounding) >= this.pos.config.sh_min_qty) {
                                this.quantity = round_pr(quant, rounding);
                                this.quantityStr = field_utils.format.float(this.quantity, { digits: [69, decimals] });
                            } else {
                                this.quantity = round_pr(quant, rounding);
                                this.quantityStr = round_pr(quant, rounding);
                                Gui.showPopup("QuantityWarningPopup", {
                                    product: this.product,
                                    quantity: round_pr(quant, rounding),
                                    product_image: this.get_image_url(this.product.id),
                                });
                            }
                        } else {
                            this.quantity = round_pr(quant, rounding);
                            this.quantityStr = field_utils.format.float(this.quantity, { digits: [69, decimals] });
                            this.product["is_added"] = false;
                        }
                    } else {
                        if (round_pr(quant, rounding) && this.pos.config.sh_show_qty_location && this.product.type == "product" && !this.product["is_added"]) {
                            if (qty_available - round_pr(quant, rounding) >= this.pos.config.sh_min_qty) {
                                this.quantity = round_pr(quant, 1);
                                this.quantityStr = this.quantity.toFixed(0);
                            } else {
                                this.quantity = round_pr(quant, 1);
                                this.quantityStr = round_pr(quant, 1);
                                Gui.showPopup("QuantityWarningPopup", {
                                    product: this.product,
                                    quantity: round_pr(quant, 1),
                                    product_image: this.get_image_url(this.product.id),
                                });
                            }
                        } else {
                            this.quantity = round_pr(quant, 1);
                            this.quantityStr = this.quantity.toFixed(0);
                            this.product["is_added"] = false;
                        }
                    }
                } else {
                    if (round_pr(quant, rounding) && this.pos.config.sh_show_qty_location && this.product.type == "product" && !this.product["is_added"]) {
                        if (qty_available - round_pr(quant, rounding) >= this.pos.config.sh_min_qty) {
                            this.quantity = quant;
                            this.quantityStr = "" + this.quantity;
                        } else {
                            this.quantity = quant;
                            this.quantityStr = quant;
                            Gui.showPopup("QuantityWarningPopup", {
                                product: this.product,
                                quantity: quant,
                                product_image: this.get_image_url(this.product.id),
                            });
                        }
                    } else {
                        this.quantity = quant;
                        this.quantityStr = "" + this.quantity;
                        this.product["is_added"] = false;
                    }
                }
            }

            // just like in sale.order changing the quantity will recompute the unit price
            if (!keep_price && !this.price_manually_set) {
                this.set_unit_price(this.product.get_price(this.order.pricelist, this.get_quantity()) + this.get_price_extra());
                this.order.fix_tax_included_price(this);
            }
            this.trigger("change", this);
        },
    });

    class ProductQtyPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            useSubEnv({ attribute_components: [] });
        }
    }
    ProductQtyPopup.template = "ProductQtyPopup";

    Registries.Component.add(ProductQtyPopup);

    class QuantityWarningPopup extends AbstractAwaitablePopup {
        constructor() {
            var parameter = super(...arguments);
            this.product_quantity = parameter.props.quantity;
            this.product = parameter.props.product;
            useSubEnv({ attribute_components: [] });
        }
        put_order() {
            var self = this;
            var selectedOrder = self.env.pos.get_order();
            self.product["is_added"] = true;
            selectedOrder.get_selected_orderline().set_quantity(this.product_quantity);
            this.trigger("close-popup");
        }
    }
    QuantityWarningPopup.template = "QuantityWarningPopup";

    Registries.Component.add(QuantityWarningPopup);

    return {
        ProductQtyPopup,
        QuantityWarningPopup,
    };
});
odoo.define("sh_pos_wh_stock.PaymentScreen", function (require) {
    "use strict";

    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");
    const { useBarcodeReader } = require("point_of_sale.custom_hooks");
    const { useListener } = require("web.custom_hooks");
    const rpc = require("web.rpc");

    const PosWHPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
            }
            async validateOrder(isForceValidate) {
                super.validateOrder(isForceValidate)
                if (this.env.pos.config.picking_type_id) {
                    var picking_type = this.env.pos.db.picking_type_by_id[this.env.pos.config.picking_type_id[0]];
                    if (picking_type && picking_type.default_location_src_id) {
                        var location_id = picking_type.default_location_src_id[0];
                        var order = this.env.pos.get_order();
                        if (location_id) {
                            var quant_by_product_id = this.env.pos.db.quant_by_product_id;
                            $.each(quant_by_product_id, function (product, value) {
                                for (var i = 0; i < order.orderlines.models.length; i++) {
                                    if (order.orderlines.models[i].product.id && order.orderlines.models[i].product.id == product) {
                                        $.each(value, function (location, qty) {
                                            if (location == location_id) {
                                                value[location] = qty - order.orderlines.models[i].quantity;
                                            }
                                        });
                                    }
                                }
                            });
                        }
                    }
                }

            }
        };

    Registries.Component.extend(PaymentScreen, PosWHPaymentScreen);
    return PosWHPaymentScreen;
});
odoo.define("sh_pos_wh_stock.ProductScreen", function (require) {
    "use strict";
    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");
    const { useBarcodeReader } = require("point_of_sale.custom_hooks");
    const { useListener } = require("web.custom_hooks");
    const ProductsWidget = require("point_of_sale.ProductsWidget");

    const WHStockProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
                useListener("click-product-image-icon", this.on_click_show_qty);
            }
            async on_click_show_qty(event) {

                const product = event.detail;
                var self = this;
                let title = product.display_name;
                let product_id = product.id;
                let quant_by_product_id = this.env.pos.db.quant_by_product_id[product_id];

                if (this.env.pos.config.sh_display_by == "location") {
                    var table_html = '<table width="100%" class="wh_qty"><thead><tr><th width="70%" class="head_td">Sucursal</th><th width="30%" class="head_td">Cantidad</th></tr></thead>';
                    var total_qty = 0;
                    $.each(quant_by_product_id, function (key, value) {
                        var location = self.env.pos.db.location_by_id[key];
                        if (value > 0) {
                            if (self.env.pos.db.lot_stock_list.includes(location["id"])) {
                                table_html += '<tr><td class="data_td">' + location["display_name"] + '</td><td class="data_td">' + value + "</td></tr>";
                                total_qty += parseInt(value);
                            } else if (location["location_id"] && self.env.pos.db.lot_stock_list.includes(location["location_id"][0])) {
                                table_html += '<tr><td class="data_td">' + location["display_name"] + '</td><td class="data_td">' + value + "</td></tr>";
                                total_qty += parseInt(value);
                            }
                        }
                    });
                    table_html += '<tr><th width="70%" class="footer_td">Total</th><th width="30%"  class="footer_td">' + total_qty + "</th></tr></table>";
                    let { confirmed, payload } = await this.showPopup("ProductQtyPopup", {
                        title: title,
                        body: table_html,
                    });

                    if (confirmed) {
                    } else {
                        return;
                    }
                } else {
                    var table_html = '<table width="100%" class="wh_qty"><thead><tr><th width="70%" class="head_td">Almacen</th><th width="30%" class="head_td">Cantidad</th></tr></thead>';
                    var total_qty = 0;
                    $.each(quant_by_product_id, function (key, value) {
                        total_qty += parseInt(value);
                        var warehouse = self.env.pos.db.warehouse_by_id[key];
                        if (warehouse) {
                            table_html += '<tr><td class="data_td">' + warehouse["name"] + "(" + warehouse["code"] + ')</td><td class="data_td">' + value + "</td></tr>";
                        }
                    });
                    table_html += '<tr><th width="70%" class="footer_td" style="text-align: right;">Total</th><th width="30%"  class="footer_td">' + total_qty + "</th></tr></table>";
                    let { confirmed, payload } = await this.showPopup("ProductQtyPopup", {
                        title: title,
                        body: table_html,
                    });

                    if (confirmed) {
                    } else {
                        return;
                    }
                }
            }
        };

    Registries.Component.extend(ProductScreen, WHStockProductScreen);

    const WHStockProductsWidget = (ProductsWidget) =>
        class extends ProductsWidget {
        	get productsToDisplay() {
                var self = this;
                var product_list_1 = []
                
                if (this.searchWord !== "") {
                    var tags = this.env.pos.db.search_tag_in_category(this.selectedCategoryId, this.env.pos.db.product_by_tag_id, this.searchWord);

                    var products = this.env.pos.db.search_product_in_category(this.selectedCategoryId, this.searchWord);
                    if (products.length > 0) {
                        this.final_suggest_prodcuts = this.get_final_suggested_product_ids(products);
                    }
                    if (this.env.pos.config.sh_search_product) {
                        if (tags.length > 0) {
                            return tags
                        }
                    }
                    if (self.env.pos.user.role != 'manager') {
                        if (this.env.pos.config.sh_enable_own_product) {
                            for (var i = 0; i < products.length; i++) {
                                var product = products[i]
                                if (product.sh_select_user.includes(self.env.pos.user.id)) {
                                    product_list_1.push(product)
                                }
                            }
                            if (product_list_1.length > 0) {
                                return product_list_1
                            } else {
                                return []
                            }
                        }else{
                        	return products
                        }
                    }else{
                    	return products
                    }
                } else {
                    var product_list = [];
                    _.each(self.env.pos.db.get_product_by_category(self.selectedCategoryId), function (product) {
                        var quant_by_product_id = self.env.pos.db.quant_by_product_id[product.id];
                        if (self.env.pos.config.sh_show_qty_location) {
                            var qty_available = quant_by_product_id ? quant_by_product_id[self.env.pos.config.sh_pos_location[0]] : 0;
                            if (qty_available) {
                                product["sh_pos_stock"] = qty_available;
                            } else {
                                product["sh_pos_stock"] = 0;
                            }
                        }
                        product_list.push(product);
                    });
                    
                    
                    if (self.env.pos.user.role != 'manager') {
                        if (this.env.pos.config.sh_enable_own_product) {
                            for (var i = 0; i < product_list.length; i++) {
                                var product = product_list[i]
                                if (product.sh_select_user.includes(self.env.pos.user.id)) {
                                    product_list_1.push(product)
                                }
                            }
                            if (product_list_1.length > 0) {
                                return product_list_1
                            } else {
                                return []
                            }
                        }else{
                        	return product_list
                        }
                    }else{
                    	return product_list
                    }
                }
            }
        };

    Registries.Component.extend(ProductsWidget, WHStockProductsWidget);
    return {
        ProductScreen,
        ProductsWidget,
    };
});
odoo.define("sh_pos_wh_stock.screens", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var core = require("web.core");
    var DB = require("point_of_sale.DB");

    var QWeb = core.qweb;
    var _t = core._t;

    models.load_models({
        model: "stock.quant",
        fields: ["id", "product_id", "location_id", "company_id", "quantity", "reserved_quantity"],
        domain: function (self) {
            return [["location_id.usage", "in", ["internal"]]];
        },
        loaded: function (self, qunats) {
            self.db.add_qunats(qunats);
        },
    });
    models.load_models({
        model: "stock.warehouse",
        fields: ["id", "lot_stock_id", "code", "name"],
        loaded: function (self, warehouses) {
            self.db.add_warehouse(warehouses);
        },
    });
    models.load_models({
        model: "stock.location",
        fields: ["id", "name", "display_name", "location_id"],
        loaded: function (self, locations) {
            self.db.add_location(locations);
        },
    });
    models.load_models({
        model: "stock.picking.type",
        fields: ["id", "name", "default_location_src_id"],
        loaded: function (self, picking_types) {
            self.db.add_picking_types(picking_types);
        },
    });
    DB.include({
        init: function (options) {
            this._super(options);
            this.qunats = [];
            this.qunat_by_id = {};
            this.quant_by_product_id = {};
            this.picking_type_by_id = {};
            this.warehouse_by_id = {};
            this.lot_stock_list = [];
            this.location_by_id = {};
        },
        add_picking_types: function (picking_types) {
            for (var i = 0, len = picking_types.length; i < len; i++) {
                var picking_type = picking_types[i];
                this.picking_type_by_id[picking_type["id"]] = picking_type;
            }
        },
        add_qunats: function (qunats) {
            if (!qunats instanceof Array) {
                qunats = [qunats];
            }
            for (var i = 0, len = qunats.length; i < len; i++) {
                var qunat = qunats[i];
                this.qunats.push(qunat);
                this.qunat_by_id[qunat.id] = qunat;
                if (qunat.product_id[0] in this.quant_by_product_id) {
                    var tmp_loc_dic = this.quant_by_product_id[qunat.product_id[0]];
                    if (qunat.location_id[0] in tmp_loc_dic) {
                        var tmp_qty = tmp_loc_dic[qunat.location_id[0]];
                        tmp_loc_dic[qunat.location_id[0]] = qunat.quantity + tmp_qty;
                    } else {
                        tmp_loc_dic[qunat.location_id[0]] = qunat.quantity;
                    }
                    this.quant_by_product_id[qunat.product_id[0]] = tmp_loc_dic;
                } else {
                    var location_qty_dic = {};
                    location_qty_dic[qunat.location_id[0]] = qunat.quantity;
                    this.quant_by_product_id[qunat.product_id[0]] = location_qty_dic;
                }
            }
        },
        add_warehouse: function (warehouses) {
            for (var i = 0, len = warehouses.length; i < len; i++) {
                var warehouse = warehouses[i];
                this.warehouse_by_id[warehouse.lot_stock_id[0]] = warehouse;
                this.lot_stock_list.push(warehouse.lot_stock_id[0]);
            }
        },
        add_location: function (locations) {
            for (var i = 0, len = locations.length; i < len; i++) {
                var location = locations[i];
                this.location_by_id[location["id"]] = location;
            }
        },
    });
});
