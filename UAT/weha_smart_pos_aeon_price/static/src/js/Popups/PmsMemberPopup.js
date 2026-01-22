odoo.define('weha_smart_pos_aeon_price.PmsMemberPopup', function(require) {
    'use strict';

    const PmsMemberPopup = require('weha_smart_pos_aeon_pms.PmsMemberPopup');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

   const AeonPricePmsMemberPopup = (PmsMemberPopup) => 
        class extends PmsMemberPopup {
            setup() {
                super.setup();
            }

            async searchCustomer(){
                await super.searchCustomer();
                var self = this;
                var order = self.env.pos.get_order();
                if(order.get_is_aeon_member()){
                    console.log("PMS Member");
                    let pdcm_pricelist = _.find(self.env.pos.pricelists, function (pricelist) {
                        return pricelist.id === self.env.pos.config.pdcm_pricelist_id[0];});
                    console.log(pdcm_pricelist);
                    if(pdcm_pricelist){
                        order.set_pricelist(pdcm_pricelist)
                    }
                }else{
                    console.log("Not PMS Member");
                }
            }

        }    

    Registries.Component.extend(PmsMemberPopup, AeonPricePmsMemberPopup);
    return PmsMemberPopup
        
});