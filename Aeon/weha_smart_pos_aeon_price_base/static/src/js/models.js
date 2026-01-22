odoo.define('weha_smart_pos_aeon_price_base.models', function(require){
   'use strict';
      
   var {  Orderline } = require('point_of_sale.models');
   const Registries = require('point_of_sale.Registries');

   const PriceBaseOrderline = (Orderline) =>
   class extends Orderline {
      constructor(obj, options) {
         super(...arguments);
         this.price_source = this.price_source || 'list_price';         
      }

      set_price_source(price_source){
         this.price_source = price_source;
      }

      get_price_source(flag){
            return this.price_source;
      }

      init_from_JSON(json){
         this.price_source = json.price_source;
         super.init_from_JSON(...arguments);
      }

      export_as_JSON(){
         var json = super.export_as_JSON();
         json.price_source = this.price_source;
         return json;
      }

      clone(){
         var orderLine = super.clone();
         orderLine.price_source = this.price_source;
         return orderLine;
      }
   }

   Registries.Model.extend(Orderline, PriceBaseOrderline);

});