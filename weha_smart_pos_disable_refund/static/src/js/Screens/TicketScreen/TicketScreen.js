odoo.define('weha_smart_pos_disable_refund.TicketScreen', function (require) {
    'use strict';
    const { onMounted, useRef, useState } = owl;
    const Registries = require('point_of_sale.Registries');
    const TicketScreen = require('point_of_sale.TicketScreen');
    const { isConnectionError } = require('point_of_sale.utils');
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');

    const DisableRefundTicketScreen = (TicketScreen) =>
        class extends TicketScreen {
            setup() {
                super.setup();
                this.posActivityLog = new PosActivityLog();
                // Don't override state, just add allowPin property
                Object.assign(this.state, { allowPin: false });
                onMounted(this.mounted);
            }

           async mounted(){
                // Call parent mounted if it exists
                if (super.mounted) {
                    await super.mounted();
                }
                console.log('getItem - allowPin');
                console.log(localStorage.getItem('allowPin'));           
                let allowPin = localStorage.getItem('allowPin');
                if (allowPin === 'true') {
                    console.log('set state allowpin')
                    this.state.allowPin = true;     
                } else {
                    this.state.allowPin = false;
                }
            }
        

            async _onDoRefund() {
                try {                    
                    const hasItems = this.getHasItemsToRefund();
                    if (!hasItems) {
                        await this.showPopup('ErrorPopup', {
                            body: this.env._t('There are no items to refund'),                    
                        });                            
                        return;
                    }
                    this.el.style.pointerEvents = 'none';                
                    const { confirmed, payload: reasonPayload } = await this.showPopup('TextInputPopup',{
                        title: this.env._t('Refund Reason'),
                        body: 'Please input refund reason!',
                    });

                    console.log('reasonPayload');
                    console.log(reasonPayload); 
                    
                    if (confirmed && reasonPayload){
                        if (this.env.pos.config.module_pos_hr && this.state.allowPin === false) {                                        
                            const employees = this.env.pos.res_users_supervisors
                            .filter((supervisor) => this.env.pos.employee_by_user_id[supervisor.id])
                            .map((supervisor) => {
                                const employee = this.env.pos.employee_by_user_id[supervisor.id]
                                return {
                                    id: employee.id,
                                    item: employee,
                                    label: employee.name,
                                    isSelected: false,
                                    fingerprintPrimary: employee.fingerprint_primary,
                                };
                            });

                            let {confirmed, payload: employee} = await this.showPopup('SupervisorGridPopup', {
                                title: this.env._t('Supervisor'),
                                employees: employees,
                            });

                            if (confirmed && employee) {
                                var order = this.env.pos.get_order();
                                var { payload: status } = await this.showPopup('FingerprintAuthPopup', {body: reasonPayload, employee: employee});
                                console.log(status);
                                if(status){                                
                                    const syncorder = this.getSelectedSyncedOrder();
                                    console.log(syncorder);
                                    await super._onDoRefund();                                
                                    const order = this.env.pos.get_order();
                                    order.set_is_refund(true);
                                    order.set_refund_parent_pos_reference(syncorder.name);
                                    console.log(order);                                    
                                    this.posActivityLog.saveLogToLocalStorage(
                                        'Ticket Screen',
                                        'Refund Transcation - ' + status,
                                        this.env.pos.user.id,
                                        order.cashier.id,
                                        this.env.pos.config.id,
                                        this.env.pos.pos_session.id,
                                        order.name
                                    );                   
                                }else{
                                    await this.showPopup('ErrorPopup', {
                                        body: this.env._t('Refund transaction failed!'),                    
                                    });       
                                }                                
                            }                                             
                        }else{
                            // Show supervisor grid first
                            const employees = this.env.pos.res_users_supervisors
                            .filter((supervisor) => this.env.pos.employee_by_user_id[supervisor.id])
                            .map((supervisor) => {
                                const employee = this.env.pos.employee_by_user_id[supervisor.id]
                                return {
                                    id: employee.id,
                                    item: employee,
                                    label: employee.name,
                                    isSelected: false,
                                    fingerprintPrimary: employee.fingerprint_primary,
                                };
                            });

                            let {confirmed: supervisorConfirmed, payload: employee} = await this.showPopup('SupervisorGridPopup', {
                                title: this.env._t('Supervisor'),
                                employees: employees,
                            });

                            if (supervisorConfirmed && employee) {
                                // Ask for PIN after selecting supervisor
                                if (employee.pin) {
                                    const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                                        isPassword: true,
                                        title: this.env._t('Password ?'),
                                        startingValue: null,
                                    });

                                    if (confirmed && employee.pin === inputPin) {
                                        const syncorder = this.getSelectedSyncedOrder();
                                        console.log(syncorder);
                                        await super._onDoRefund();                                
                                        const order = this.env.pos.get_order();
                                        order.set_is_refund(true);
                                        order.set_refund_parent_pos_reference(syncorder.name);
                                        console.log(order);
                                        this.posActivityLog.saveLogToLocalStorage('Ticket Screen','Refund Transaction',order.cashier.id);
                                    } else {
                                        await this.showPopup('ErrorPopup', {
                                            body: this.env._t('Incorrect Password'),                    
                                        });
                                    }
                                } else {
                                    const syncorder = this.getSelectedSyncedOrder();
                                    console.log(syncorder);
                                    await super._onDoRefund();                                
                                    const order = this.env.pos.get_order();
                                    order.set_is_refund(true);
                                    order.set_refund_parent_pos_reference(syncorder.name);
                                    console.log(order);
                                    this.posActivityLog.saveLogToLocalStorage('Ticket Screen','Refund Transaction',order.cashier.id);
                                }
                            } else {
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Refund transaction failed!'),                    
                                });
                            }                          
                        }      
                    }else{
                        throw new Error('Refund reason is required');
                    }
                } catch (error) {
                    if (isConnectionError(error)) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Network Error'),
                            body: this.env._t('Unable to refund order.'),
                        });
                    } else {
                        throw error;
                    }
                } finally {
                    this.el.style.pointerEvents = 'auto';
                }                
            }            
        }
            
    Registries.Component.extend(TicketScreen, DisableRefundTicketScreen);


});