odoo.define('aspl_pos_wallet.ReceiptScreen', function(require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const PosResReceiptScreen = ReceiptScreen =>
        class extends ReceiptScreen {
            constructor(){
               super(...arguments);
               this.get_remaining_wallet_amount();
            }
            async get_remaining_wallet_amount(){
                var self = this
                if (this.env.pos.get_order().get_client()){
                    await this.rpc({
                        model: "res.partner",
                        method: "search_read",
                        domain: [['id', '=', this.env.pos.get_order().get_client().id]],
                        fields:['remaining_wallet_amount','write_date']
                    },{async: false}).then(function(result){
                        if(result){
                            if(result){
                                let new_partner = _.extend(self.env.pos.get_order().get_client(),result[0]);
                                self.env.pos.db.add_partners(new_partner);
                            }
                        }
                    });
                }
            }
        };

    Registries.Component.extend(ReceiptScreen, PosResReceiptScreen);

    return ReceiptScreen;
});