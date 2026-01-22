odoo.define('weha_customer_deposit.ReceiptScreen', function(require) {
    'use strict';

    var rpc = require('web.rpc');
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const DepositReceiptScreen = ReceiptScreen =>
        class extends ReceiptScreen {
            constructor(){
               super(...arguments);
               this.get_remaining_deposit_amount();
            }
            async get_remaining_deposit_amount(){
                var self = this
                if (this.env.pos.get_order().get_partner()){
                    await rpc.query({
                        model: "res.partner",
                        method: "search_read",
                        domain: [['id', '=', self.env.pos.get_order().get_partner().id]],
                        fields:['remaining_deposit_amount']
                    },{async: false}).then(function(result){
                        if(result){   
                            let new_partner = _.extend(self.env.pos.get_order().get_partner(),result[0]);
                            self.env.pos.db.add_partners(new_partner);                                                
                        }
                    });
                }
            }
        };

    Registries.Component.extend(ReceiptScreen, DepositReceiptScreen);

    return ReceiptScreen;
});