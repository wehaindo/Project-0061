odoo.define('weha_smart_pos_aeon_queue_busting.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    const { useBarcodeReader } = require('point_of_sale.custom_hooks');

    const QueueBustingProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            setup() {
                super.setup();
                useListener('click-busting', this._onClickBusting);
                useBarcodeReader({
                    busting: this._barcodeBustingAction,
                });
            }
            async _barcodeBustingAction(code) {               
                console.log(code);
                var self = this;
                var bustingData = code.base_code.substring(3);               
                var arr_trans = bustingData.split('|');
                var item_count = arr_trans.length;
                var item_valid_count = 0;
                var item_success_count = 0;                
                var arr_failed_barcode = '';
                arr_trans.forEach(function(trans){
                    var arr_trans = trans.split(',');
                    if(arr_trans[0] != '999999999999999999'){
                        item_valid_count = item_valid_count + 1;
                        var product = self.env.pos.db.product_by_barcode[arr_trans[0]]
                        if(product){
                            item_success_count = item_success_count + 1;
                            self.currentOrder.add_product(product, {
                                quantity: parseInt(arr_trans[1]),
                            });
                        }else{
                            arr_failed_barcode = arr_failed_barcode + arr_trans[0] + '\n';
                            console.log('Product not found')
                        }
                    }                                        
                });                 
                if(item_valid_count != item_success_count){
                    let body_text = item_success_count + " of " + item_valid_count + " items have been processed succefully \n";                     
                    body_text = body_text + 'List of Failed Barcode \n';
                    body_text = body_text + arr_failed_barcode;
                    this.showPopup('ErrorPopup', 
                        {   
                            'title': 'Scan Queue Busting Error',
                            'body': body_text,
                        }
                    );       
                }                
            }
            async _onClickBusting() {
                if (this.env.pos.get_order().orderlines.some(line => line.get_product().tracking !== 'none' && !line.has_valid_product_lot()) && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots)) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Some Serial/Lot Numbers are missing'),
                        body: this.env._t('You are trying to sell products with serial/lot numbers, but some of them are not set.\nWould you like to proceed anyway?'),
                        confirmText: this.env._t('Yes'),
                        cancelText: this.env._t('No')
                    });
                    if (confirmed) {
                        this.showScreen('TicketBustingScreen');
                    }
                } else {
                    this.showScreen('TicketBustingScreen');
                }
            }
        };

    Registries.Component.extend(ProductScreen, QueueBustingProductScreen);

    return ProductScreen;
});
