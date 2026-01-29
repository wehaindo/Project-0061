odoo.define('weha_smart_pos_aeon_pos_order_line.DeleteOrderLinesAll', function(require) {
'use strict';
   const { useState, useRef, onPatched, onMounted } = owl;
   const { Gui } = require('point_of_sale.Gui');
   const PosComponent = require('point_of_sale.PosComponent');
   const { identifyError } = require('point_of_sale.utils');
   const ProductScreen = require('point_of_sale.ProductScreen');
   const { useListener } = require("@web/core/utils/hooks");
   const Registries = require('point_of_sale.Registries');
   const PaymentScreen = require('point_of_sale.PaymentScreen');
   const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');

   class OrderLineClearALL extends PosComponent {
       setup() {
            super.setup();
            this.posActivityLog = new PosActivityLog();
            useListener('click', this.onClick);
            this.state = useState({allowPin:false});
            onMounted(this.mounted);
       }
       
        mounted(){
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
    
       getUTCFormattedDateTime() {
            const now = new Date();
        
            const year = now.getUTCFullYear();
            const month = String(now.getUTCMonth() + 1).padStart(2, '0'); // Months are zero-based
            const day = String(now.getUTCDate()).padStart(2, '0');
        
            const hours = String(now.getUTCHours()).padStart(2, '0');
            const minutes = String(now.getUTCMinutes()).padStart(2, '0');
            const seconds = String(now.getUTCSeconds()).padStart(2, '0');
        
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
       }

       getFormattedDateTime() {
            const now = new Date();
        
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0'); // Months are zero-based
            const day = String(now.getDate()).padStart(2, '0');
        
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
        
            return `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`;
       } 

       async onClick() {
            const {payload: reasonPayload} = await this.showPopup("TextInputPopup", {
                    title: this.env._t('Clear Orders?'),
                    body: this.env._t(`[${this.env.pos.get_cashier().name} on ${this.getFormattedDateTime()}]  want to delete all orders from the cart?`),
            });

            if(reasonPayload){
                if (this.env.pos.config.module_pos_hr) {
                    console.log('Check allowPin state');
                    console.log(this.state.allowPin);
                    if (!this.state.allowPin) {
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
                            var { payload: status } = await this.showPopup('FingerprintAuthPopup', {employee: employee});
                            console.log(status);
                            if(status){                                                                                
                                var order    = this.env.pos.get_order();
                                var lines    = order.get_orderlines();
                                lines.filter(line => line.get_product()).forEach(line => order.remove_orderline(line));                                        
                                this.posActivityLog.saveLogToLocalStorage(
                                    'Product Screen',
                                    'Clear Order All - ' + reasonPayload,
                                    this.env.pos.user.id,
                                    order.cashier.id,
                                    this.env.pos.config.id,
                                    this.env.pos.pos_session.id,
                                    order.name
                                );                            
                            }else{
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Clear Order All  failed!'),                    
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
                                    var order    = this.env.pos.get_order();
                                    var lines    = order.get_orderlines();
                                    lines.filter(line => line.get_product()).forEach(line => order.remove_orderline(line));                                        
                                    this.posActivityLog.saveLogToLocalStorage(
                                        'Product Screen',
                                        'Clear Order All - ' + reasonPayload,
                                        this.env.pos.user.id,
                                        order.cashier.id,
                                        this.env.pos.config.id,
                                        this.env.pos.pos_session.id,
                                        order.name
                                    );
                                } else {
                                    await this.showPopup('ErrorPopup', {
                                        body: this.env._t('Incorrect Password'),                    
                                    });
                                }
                            } else {
                                var order    = this.env.pos.get_order();
                                var lines    = order.get_orderlines();
                                lines.filter(line => line.get_product()).forEach(line => order.remove_orderline(line));                                        
                                this.posActivityLog.saveLogToLocalStorage(
                                    'Product Screen',
                                    'Clear Order All - ' + reasonPayload,
                                    this.env.pos.user.id,
                                    order.cashier.id,
                                    this.env.pos.config.id,
                                    this.env.pos.pos_session.id,
                                    order.name
                                );
                            }
                        } else {
                            await this.showPopup('ErrorPopup', {
                                body: this.env._t('Clear Order All failed!'),                    
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
                                var order    = this.env.pos.get_order();
                                var lines    = order.get_orderlines();
                                lines.filter(line => line.get_product()).forEach(line => order.remove_orderline(line));                                        
                                this.posActivityLog.saveLogToLocalStorage(
                                    'Product Screen',
                                    'Clear Order All - ' + reasonPayload,
                                    this.env.pos.user.id,
                                    order.cashier.id,
                                    this.env.pos.config.id,
                                    this.env.pos.pos_session.id,
                                    order.name
                                );
                            } else {
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Incorrect Password'),                    
                                });
                            }
                        } else {
                            var order    = this.env.pos.get_order();
                            var lines    = order.get_orderlines();
                            lines.filter(line => line.get_product()).forEach(line => order.remove_orderline(line));                                        
                            this.posActivityLog.saveLogToLocalStorage(
                                'Product Screen',
                                'Clear Order All - ' + reasonPayload,
                                this.env.pos.user.id,
                                order.cashier.id,
                                this.env.pos.config.id,
                                this.env.pos.pos_session.id,
                                order.name
                            );
                        }
                    } else {
                        await this.showPopup('ErrorPopup', {
                            body: this.env._t('Clear Order All failed!'),                    
                        });
                    }
                    
                }
            }            
       }

   }

   OrderLineClearALL.template = 'OrderLineClearALL';
   ProductScreen.addControlButton({
       component: OrderLineClearALL,
       condition: function() {
           return this.env.pos;
       },
   });
   Registries.Component.add(OrderLineClearALL);
   return OrderLineClearALL;
});