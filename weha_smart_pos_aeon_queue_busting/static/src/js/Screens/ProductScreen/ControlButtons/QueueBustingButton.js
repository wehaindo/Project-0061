odoo.define('weha_smart_pos_aeon_queue_busting.QueueBustingButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class QueueBustingButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }

        async onClick() {
            var self = this;
            const { confirmed, payload: bustingData } = await this.showPopup('TextAreaPopup', {'title': 'Scan Busting Receipt'});
            if(confirmed){
                console.log(bustingData);
                var arr_trans = bustingData.split('|');
                console.log(arr_trans);
                arr_trans.forEach(function(trans){
                    var arr_trans = trans.split(',');
                    console.log(arr_trans[0]);
                    console.log(arr_trans[1]);
                    if (arr_trans[0] != '999999999999999999'){
                        var product = self.env.pos.db.product_by_barcode[arr_trans[0]]
                        if(product){
                            self.currentOrder.add_product(product, {
                                quantity: parseInt(arr_trans[1]),
                            });
                        }else{
                            console.log('Product not found')
                        }                    
                    }else{
                        console.log('ignore');
                    }
                });                
            }            
        }
    }
    QueueBustingButton.template = 'QueueBustingButton';

    ProductScreen.addControlButton({
        component: QueueBustingButton,
        condition: function() {
            return false;
        },
    });

    Registries.Component.add(QueueBustingButton);

    return QueueBustingButton;
});