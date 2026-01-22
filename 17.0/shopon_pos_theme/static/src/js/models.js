odoo.define("shopon_pos_theme.models", function (require) {
  "use strict";
  var core = require("web.core");
  var rpc = require("web.rpc");
  const { Gui } = require("point_of_sale.Gui");
  const Registries = require("point_of_sale.Registries");
  var _t = core._t;
  var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
  const ProductScreen = require('point_of_sale.ProductScreen');

  const PosStock = (PosGlobalState) => class PosStock extends PosGlobalState {
    async _processData(loadedData) {
         await super._processData(...arguments);
            var self = this;
    }
    async _loadProductProduct(products) {
        super._loadProductProduct(products.filter(p=>p.is_loyalty_reward_products));
      var self = this;
      await rpc.query({
        model: "res.config.settings",
        method: "setu_pos_fetch_pos_stock",
        args: [{
          setu_stock_type: self.config.setu_stock_type,
          setu_hide_out_of_stock: self.config.setu_hide_out_of_stock,
          config_id: self.config.id,
        }],
      })
        .then(function (result) {
          self.setu_product_qtys = result;
          self.db.setu_product_qtys = result;
          self.db.setu_hide_out_of_stock = self.config.setu_hide_out_of_stock;
        });
      if (self.config.setu_display_stock) {
        if(self.config.setu_hide_out_of_stock){
                return super._loadProductProduct(products.filter(p=>(self.db.setu_product_qtys[p.id] || p.is_loyalty_reward_products)))
        }
        else{
            return super._loadProductProduct(products);
        }
      }
      self.setu_change_qty_css();
      super._loadProductProduct(products);
    }

    push_single_order(order, opts) {
      var self = this;
      if (order) {
        if (!order.is_return_order) {
          var setu_order_line = order.get_orderlines();
          for (var j = 0; j < setu_order_line.length; j++) {
            if (!setu_order_line[j].stock_location_id)
              self.setu_product_qtys[setu_order_line[j].product.id] =
                self.setu_product_qtys[setu_order_line[j].product.id] -
                setu_order_line[j].quantity;
          }
        } else {
          var setu_order_line = order.get_orderlines();
          for (var j = 0; j < setu_order_line.length; j++) {
            self.setu_product_qtys[setu_order_line[j].product.id] =
              self.setu_product_qtys[setu_order_line[j].product.id] +
              setu_order_line[j].quantity;
          }
        }
      }
      return super.push_single_order(...arguments);
    }
    push_orders(order, opts) {
      var self = this;
      if (order) {
        if (!order.is_return_order) {
          var setu_order_line = order.get_orderlines();
          for (var j = 0; j < setu_order_line.length; j++) {
            if (!setu_order_line[j].stock_location_id)
              self.setu_product_qtys[setu_order_line[j].product.id] =
                self.setu_product_qtys[setu_order_line[j].product.id] -
                setu_order_line[j].quantity;
          }
        } else {
          var setu_order_line = order.get_orderlines();
          for (var j = 0; j < setu_order_line.length; j++) {
            self.setu_product_qtys[setu_order_line[j].product.id] =
              self.setu_product_qtys[setu_order_line[j].product.id] +
              setu_order_line[j].quantity;
          }
        }
      }
      return super.push_orders(...arguments);
    }
    set_stock_qtys(result) {
      var self = this;
      var all = $(".product");
      if (result){
      $.each(all, function (index, value) {
        var product_id = $(value).data("product-id");
        var stock_qty = result[product_id];
        $(value).find(".qty-tag").html(stock_qty);
      });
      }
    }
    get_information(setu_product_id) {
      this.setu_change_qty_css();
      if (this.env.pos.setu_product_qtys)
        return this.env.pos.setu_product_qtys[setu_product_id];
    }
    setu_change_qty_css() {
      var self = this;
      var setu_order = self.orders;
      var setu_p_qty = new Array();
      var setu_product_obj = self.setu_product_qtys;
      if (setu_order) {
        for (var i in setu_product_obj)
          setu_p_qty[i] = self.setu_product_qtys[i];
        for (var i = 0; i < setu_order.length; i++) {
          if (!setu_order[i].is_return_order) {
            var setu_order_line = setu_order[i].get_orderlines();
            for (var j = 0; j < setu_order_line.length; j++) {
              if (!setu_order_line[j].stock_location_id)
                setu_p_qty[setu_order_line[j].product.id] = setu_p_qty[setu_order_line[j].product.id] - setu_order_line[j].quantity;
              var qty = setu_p_qty[setu_order_line[j].product.id];
              if (qty) {
                $(".qty-tag" + setu_order_line[j].product.id).html(qty);
              }
              else {
                $(".qty-tag" + setu_order_line[j].product.id).html("0");
              }
            }

          }
        }
      }
    }
  }
  Registries.Model.extend(PosGlobalState, PosStock);

  const PosStockOrder = (Order) => class PosStockOrder extends Order {
    add_product(product, options) {
      var self = this;
      options = options || {};
      for (var i = 0; i < this.orderlines; i++) {
        if ((self.orderlines[i].product.id == product.id) && self.orderlines[i].stock_location_id) {
          options.merge = false;
        }
      }
      if (
        !self.pos.config.setu_continous_sale && self.pos.config.setu_display_stock &&
        !self.pos.get_order().is_return_order
      ) {
        var qty_count = 0;
        if (parseInt($(".qty-tag" + product.id).html()))
          qty_count = parseInt($(".qty-tag" + product.id).html());
        else {
          var setu_order = self.pos.orders;
          var setu_p_qty = new Array();
          var qty;
          var setu_product_obj = self.pos.setu_product_qtys;
          if (setu_order) {
            for (var i in setu_product_obj)
              setu_p_qty[i] = self.pos.setu_product_qtys[i];
            _.each(setu_order, function (order) {
              var orderline = order.orderlines;
              if (orderline.length > 0)
                _.each(orderline, function (line) {
                  if (!line.stock_location_id && product.id == line.product.id)
                    setu_p_qty[line.product.id] =
                      setu_p_qty[line.product.id] - line.quantity;
                });
            });
            qty = setu_p_qty[product.id];
          }
          qty_count = qty || 0;
        }
        if (qty_count <= self.pos.config.setu_deny_val)
          Gui.showPopup("OutOfStockMessagePopup", {
            title: _t("Warning !!!!"),
            body: _t(
              "(" + product.display_name + ")" +
              self.pos.config.setu_error_msg + "."
            ),
            product_id: product.id,
          });
        else super.add_product(...arguments);
      } else super.add_product(...arguments)
      if (self.pos.config.setu_display_stock && !self.is_return_order)
        self.pos.setu_change_qty_css();
    }
  }
  Registries.Model.extend(Order, PosStockOrder);

  const PosStockOrderline = (Orderline) => class PosStockOrderline extends Orderline {
    constructor(obj, options) {
      super(...arguments);
      this.setu_line_stock_qty = 0.0;
      if (options.product)
        this.setu_line_stock_qty = parseInt(
          $(".qty-tag" + options.product.id).html()
        );
    }
    set_quantity(quantity, keep_price) {
      var self = this;
      // -------code for POS Warehouse Management----------------
      if (self.stock_location_id && quantity && quantity != "remove") {
        if (
          self.pos.get_order() &&
          self.pos.get_order().selected_orderline &&
          self.pos.get_order().selected_orderline.cid == self.cid
        ) {
          Gui.showPopup("OutOfStockMessagePopup", {
            title: _t("Warning !!!!"),
            body: _t(
              "Selected orderline product have different stock location, you can't update the qty of this orderline"
            ),
            product_id: self.product.id,
          });
          $(".numpad-backspace").trigger("update_buffer");
          return;
        } else {
          return super.set_quantity(...arguments);
        }
      }
      // -------code for POS Warehouse Management----------------
      if (
        !self.pos.config.setu_continous_sale &&
        self.pos.config.setu_display_stock &&
        isNaN(quantity) != true &&
        quantity != "" &&
        parseFloat(self.setu_line_stock_qty) - parseFloat(quantity) <
        self.pos.config.setu_deny_val &&
        self.setu_line_stock_qty != 0.0
      ) {
        Gui.showPopup("OutOfStockMessagePopup", {
          title: _t("Warning !!!!"),
          body: _t("(" + this.product.display_name + ")" + self.pos.config.setu_error_msg + "."),
          product_id: this.product.id,
        });
        $(".numpad-backspace").trigger("update_buffer");
        if (self.pos.config.setu_display_stock) self.pos.setu_change_qty_css();
      } else {
        var setu_avail_pro = 0;
        if (self.pos.selectedOrder) {
          var setu_pro_order_line = self.pos.selectedOrder.get_selected_orderline();
          if (!self.pos.config.setu_continous_sale && self.pos.config.setu_display_stock && setu_pro_order_line) {
            var setu_current_qty = parseInt($(".qty-tag" + setu_pro_order_line.product.id).html());
            if (quantity == "" || quantity == "remove")
              setu_avail_pro = setu_current_qty + setu_pro_order_line;
            else setu_avail_pro = setu_current_qty + setu_pro_order_line - quantity;
            if (self.pos.config.setu_display_stock) self.pos.setu_change_qty_css();
            if (setu_avail_pro < self.pos.config.setu_deny_val && !(quantity == "" || quantity == "remove")) {
              Gui.showPopup("OutOfStockMessagePopup", {
                title: _t("Warning !!!!"),
                body: _t("(" + setu_pro_order_line.product.display_name + ")" + self.pos.config.setu_error_msg + "."),
                product_id: setu_pro_order_line.product.id,
              });
            } else {
              var result = super.set_quantity(...arguments);
              if (self.pos.config.setu_display_stock) self.pos.setu_change_qty_css();
              return result
            }
          } else {
            var result = super.set_quantity(...arguments);
            if (self.pos.config.setu_display_stock) self.pos.setu_change_qty_css();
            return result
          }
        } else {
          var result = super.set_quantity(...arguments);
          if (self.pos.config.setu_display_stock) self.pos.setu_change_qty_css();
          return result
        }
      }
    }
  }
  Registries.Model.extend(Orderline, PosStockOrderline);
});
