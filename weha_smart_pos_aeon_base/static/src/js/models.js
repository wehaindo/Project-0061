odoo.define('weha_smart_pos_aeon_base.models', function(require){
    "use strict";

    var { PosCollection, PosGlobalState, Order, Orderline, Payment, PosModel } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const AeonMemberOrder = (Order) => 
        class extends Order {
            constructor(obj, options) {
                super(...arguments);
                this.is_aeon_member = this.is_aeon_member || false;                
                this.card_no = this.card_no || false;
                this.aeon_member = this.aeon_member || false;
                this.aeon_member_day = this.aeon_member_day || false;
                this.is_void_order = this.is_void_order || false;
            }

            init_from_JSON(json) {
                super.init_from_JSON(...arguments);
                this.is_aeon_member = json.is_aeon_member
                this.card_no = json.card_no;
                this.aeon_member = json.aeon_member;
                this.aeon_member_day = json.aeon_member_day;
                this.is_void_order = json.is_void_order;
            }

