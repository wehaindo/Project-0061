odoo.define('weha_smart_pos_base.TicketScreen', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const TicketScreen = require('point_of_sale.TicketScreen');

    const BaseTicketScreen = (TicketScreen) =>
        class extends TicketScreen {
            constructor() {
                super(...arguments);
            }

            async _onDoRefund() {
                try {
                    this.el.style.pointerEvents = 'none';                
                    const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                        title: this.env._t('Supervisor Pin?'),                    
                        isInputSelected: true,                        
                    }); 
    
                    if ( confirmed ){
                        var supervisor = this.env.pos.res_users_supervisor_by_rfid[payload];
                        if (supervisor) {
                            const order = this.getSelectedSyncedOrder();
                            order.set_is_refund(true);
                            order.set_refund_parent_pos_reference(order.name);
                            super._onDoRefund();
                        }else{
                            await this.showPopup('ErrorPopup', {
                                body: this.env._t('Refund transaction failed!'),                    
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
            
    Registries.Component.extend(TicketScreen, BaseTicketScreen);


});