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
  }
  Registries.Model.extend(PosGlobalState, PosStock);

  const PosStockOrder = (Order) => class PosStockOrder extends Order {
    add_product(product, options) {
      super.add_product(...arguments);
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
