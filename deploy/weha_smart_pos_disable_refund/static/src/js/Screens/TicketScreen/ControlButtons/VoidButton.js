odoo.define('weha_smart_pos_disable_refund.VoidButton', function (require) {
    'use strict';

    const { useListener } = require("@web/core/utils/hooks");
    const { isConnectionError } = require('point_of_sale.utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class VoidButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this._onClick);
        }

        get commandName() {
            return this.env._t('Void');
        }

        init_data(order, void_order){
            if(order.get_partner()){
                void_order.set_partner(order.get_partner());
            }
        }

        set_options(line){
            const options = {
                quantity: line.quantity * -1,
                price: line.price,
                extras: { price_manually_set: true },
                merge: false,
                refunded_orderline_id: line.id,
                tax_ids: line.tax_ids,
                discount: line.discount,
                refunded_qty: line.quantity
            }
            return options;
        }

        async add_orderlines(order, void_order){
            for (const line of order.orderlines) {                
                const product = this.env.pos.db.get_product_by_id(line.product.id);                
                const options = this.set_options(line);   
                await void_order.add_product(product, options);
            }
        }

        add_payments(order, void_order){
            console.log('weha_smart_pos_disable_refund.VoidButton.add_payment');
        }

        async _voidOrder() {
            // define partner -> generate orderline -> define payment
            var order = this.props.order;
            console.log("order refund")
            console.log(order);            
            if (!order) return;
            const void_order = this.env.pos.add_new_order();
            this.init_data(order, void_order);
            await this.add_orderlines(order, void_order);
            this.add_payments(order,void_order);
            this.env.pos.set_order(void_order);
            this.showScreen('ProductScreen');
            // const orderId = order.backendId;
        }

        async _onClick() {
            try {
                this.el.style.pointerEvents = 'none';                
                const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                    title: this.env._t('Supervisor Pin?'),                    
                    isInputSelected: true,                        
                }); 

                if ( confirmed ){
                    var supervisor = this.env.pos.res_users_supervisor_by_rfid[payload];
                    if (supervisor) {
                        await this._voidOrder();
                    }else{
                        await this.showPopup('ErrorPopup', {
                            body: this.env._t('Void transaction failed!'),                    
                        });       
                    }
                }                
            } catch (error) {
                if (isConnectionError(error)) {
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Network Error'),
                        body: this.env._t('Unable to void order.'),
                    });
                } else {
                    throw error;
                }
            } finally {
                this.el.style.pointerEvents = 'auto';
            }
        }
    }
    VoidButton.template = 'VoidButton';
    Registries.Component.add(VoidButton);

    return VoidButton;
});