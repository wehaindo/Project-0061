odoo.define('weha_smart_pos_aeon_price.OrderlineDetails', function (require) {
    "use strict";
    
    var OrderlineDetails = require('point_of_sale.OrderlineDetails');
    var models = require('point_of_sale.models');
    var Orderline = models.Orderline;
    const Registries = require('point_of_sale.Registries');

    var AeonPriceOrderlineDetails = OrderlineDetails => class extends OrderlineDetails {
        
        get_price_source(){
            return this.props.line.price_source;
        }

        get_prc_no(){
            console.log(this.props.line);
            return this.props.line.prc_no;
        }

    }

    Registries.Component.extend(OrderlineDetails, AeonPriceOrderlineDetails);


})