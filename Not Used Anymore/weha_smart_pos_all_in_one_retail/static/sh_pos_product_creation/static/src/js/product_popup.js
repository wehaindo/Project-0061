odoo.define("sh_pos_product_creation.Product_popup", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const { ProductsWidget } = require("point_of_sale.ProductsWidget");
    var rpc = require("web.rpc");
    var models = require("point_of_sale.models");
    var DB = require("point_of_sale.DB");
    var utils = require("web.utils");

    models.load_models({
        model: "product.category",
        fields: [],
        loaded: function (self, product_categorie) {
            self.product_categorie = product_categorie;
        },
    });
    models.load_models({
        model: "pos.category",
        fields: [],
        loaded: function (self, pos_category) {
            self.pos_category = pos_category;
        },
    });

    DB.include({
        init: function (options) {
            this._super.apply(this, arguments);
            this.all_product = [];
        },
        get_all_product: function () {
            return this.all_product;
        },
    });

    class Product_popup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }
        mounted() {
            $(".category_name").hide();
            $("#add_category").hide();
            $("#product_category").change(function () {
                if ($("#product_category option:selected").val() == "newCategory") {
                    $(".category_name").show();
                    $("#add_category").show();
                } else {
                    $(".category_name").hide();
                    $("#add_category").hide();
                }
            });
        }
        addCategory() {
            var self = this;
            var cnm = $(".category_name").val();
            rpc.query({
                model: "product.category",
                method: "create",
                args: [
                    {
                        name: cnm,
                        display_name: cnm,
                    },
                ],
            }).then(function (callback) {
                var new_category = {};
                if (callback) {
                    new_category["id"] = callback;
                    new_category["display_name"] = cnm;
                    self.env.pos.product_categorie.push(new_category);
                }
                self.render();
                $(".category_name").hide();
                $("#add_category").hide();

                setTimeout(function () {
                    $(document)
                        .find('#product_category option[value="' + callback + '"]')
                        .attr("selected", "selected");
                }, 100);
            });
        }
        createProduct() {
            var self = this;
            var name = $(".name").val();
            var sold = document.getElementById("sold").checked;
            var purchase = document.getElementById("purchase").checked;
            var product_type = $(".produc_type option:selected").val();
            var product_category = $("#product_category option:selected").val();
            var pos_category = $(".pos_category option:selected").val();
            var reference = $(".reference").val();
            
            
            var price = parseInt($("#price").val());
            var cost = parseInt($("#cost").val());
            var available_in_pos = $(".available_in_pos").val();
            var note = $(".note").val();

            var product_vals = {
                name: name,
                display_name: name,
                sale_ok: sold,
                purchase_ok: purchase,
                type: product_type,
                categ_id: parseInt(product_category),
                default_code: reference,
                
                list_price: price,
                lst_price: price,
                standard_price: parseInt(cost),
                pos_categ_id: parseInt(pos_category),
                available_in_pos: available_in_pos,
                description: note,
            };
            if($(".barcode").val() != ""){
                product_vals['barcode'] = $(".barcode").val()
            }
            product_vals['suggestion_line'] = [];

            if (name) {
                if (price > 0) {
                    if (cost > 0 || cost >= 0) {
                        rpc.query({
                            model: "product.product",
                            method: "create_pos_product",
                            args: [product_vals],
                        }).then(function (products) {
                            if(products.sale_ok){
                                self.env.pos.db.add_products(
                                    _.map([products], function (product) {
                                        product["pos"] = self.env.pos;
                                        product.categ = _.findWhere(self.env.pos.product_categories, { id: parseInt(product.categ_id[0]) });

                                        return new models.Product({}, product);
                                    })
                                );
                                $(".fa-home").click();
                            }
                        });
                        this.trigger("close-popup");
                    } else {
                        alert("Enter Valid cost ");
                        $("#cost").focus();
                    }
                } else {
                    alert("Enter Valid price ");
                    $("#price").focus();
                }
            } else {
                alert("Enate Product Name");
                $(".name").focus();
            }
        }
        cancelProduct() {
            this.trigger("close-popup");
        }
    }

    Product_popup.template = "Product_popup";

    Registries.Component.add(Product_popup);

    return Product_popup;
});
