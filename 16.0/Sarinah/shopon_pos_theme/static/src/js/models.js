odoo.define("shopon_pos_theme.models", function (require) {
  "use strict";
  var core = require("web.core");
  var rpc = require("web.rpc");
  const { Gui } = require("point_of_sale.Gui");
  const Registries = require("point_of_sale.Registries");
  var _t = core._t;
  // const models = require('point_of_sale.models');
  var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');  
  const ProductScreen = require('point_of_sale.ProductScreen');


  const OrderSuper = Order.prototype;

  const PosStock = (PosGlobalState) => class PosStock extends PosGlobalState {
    async _processData(loadedData) {
         await super._processData(...arguments);
            var self = this;
    }        
  }
  Registries.Model.extend(PosGlobalState, PosStock);

  const PosStockOrder = (Order) => class PosStockOrder extends Order {
    add_product(product, options) {
      var self = this;
      var quantity = 1;
      const order = this.pos.get_order();
      rpc.query({
        model: 'product.product',
        method: 'get_product_info_pos',
        args: [[product.id],
          product.get_price(order.pricelist, quantity),
          quantity,
          this.pos.config.id],
        // kwargs: {context: this.env.session.user_context},
      }).then(function(product_info) {
        console.log(product_info);
        OrderSuper.add_product.call(self, product, options);
        // if (stock_qty <= 0) {
        //     self.pos.gui.show_popup('error', {
        //         'title': _t('Insufficient Stock'),
        //         'body': _t('The selected variant of the product is out of stock at this location.'),
        //     });
        // } else {
        //   OrderSuper.add_product.call(self, product, options);
        // }
      }).catch(function(error){
        self.pos.gui.show_popup('error', {
          'title': _t('Check Stock Availablitiy'),
          'body': _t(error),
        });
      });
    }
  }
  Registries.Model.extend(Order, PosStockOrder);

  const PosStockOrderline = (Orderline) => class PosStockOrderline extends Orderline {
    constructor(obj, options) {
      super(...arguments);            
    }
  }
  Registries.Model.extend(Orderline, PosStockOrderline);
});
