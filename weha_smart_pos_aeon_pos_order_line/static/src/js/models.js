odoo.define('weha_smart_pos_aeon_pos_order_line.models', function(require){
    "use strict";

    var models = require('point_of_sale.models');
    var { Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');


    const AeonPosOrderLine = (Orderline) => 
        class extends Orderline {
            constructor(obj, options) {
                super(...arguments);
                this.allowDelete = this.allowDelete || true;
            }

            set_allow_delete(allowDelete){
                this.allowDelete = allowDelete
            }

            get_allow_delete(){
                return this.allowDelete;
            }


            init_from_JSON(json){
                super.init_from_JSON(...arguments);
                this.allowDelete = json.allowDelete;                
            }

            export_as_JSON(){
                var json = super.export_as_JSON();
                json.allowDelete = this.allowDelete;
                return json;
            }

             clone(){
                var orderLine = super.clone();
                orderLine.allowDelete = this.allowDelete;
                return orderLine;
            }
        }

    Registries.Model.extend(Orderline, AeonPosOrderLine);
});