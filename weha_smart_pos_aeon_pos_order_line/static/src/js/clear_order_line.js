           
odoo.define('weha_smart_pos_aeon_pos_order_line.DeleteOrderLines', function(require) {
'use strict';
    const { useState, useRef, onPatched, onMounted } = owl;
    const { useListener } = require("@web/core/utils/hooks");
    const { onChangeOrder } = require('point_of_sale.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const Orderline = require('point_of_sale.Orderline');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const OrderWidget = require('point_of_sale.OrderWidget');
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');


    const OrderLineDelete = (Orderline) =>
       class extends Orderline {
            constructor(obj, options) {
                super(...arguments);
                this.posActivityLog = new PosActivityLog();
                this.allowDelete = this.allowDelete || true;
                this.allowPin = false;
                let lsAllowPin = localStorage.getItem('allowPin');                   
                if (lsAllowPin === 'true') {
                    console.log('set state allowpin')
                    this.allowPin = true;     
                }                 
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
        

            set_allow_delete(allowDelete){
                this.allowDelete = allowDelete
            }

            get_allow_delete(){
                return this.allowDelete;
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

            async deleteLine() {
                const {payload: reasonPayload} = await this.showPopup("TextInputPopup", {
                    title: this.env._t('Clear Orders?'),
                    body: this.env._t(`[${this.env.pos.get_cashier().name} on ${this.getFormattedDateTime()}]  want to delete this order line from the cart?`),
                });
                if(reasonPayload){           
                    if (this.env.pos.config.module_pos_hr) {                                                                    
                        if (!this.allowPin){
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
                                    order.remove_orderline(this.props.line);
                                    this.posActivityLog.saveLogToLocalStorage(
                                        'Product Screen',
                                        'Delete Orderline - ' + reasonPayload,
                                        this.env.pos.user.id,
                                        order.cashier.id,
                                        this.env.pos.config.id,
                                        this.env.pos.pos_session.id,
                                        order.name
                                    );                            
                                }else{
                                    await this.showPopup('ErrorPopup', {
                                        body: this.env._t('Delete orderline failed!'),                    
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
                                        order.remove_orderline(this.props.line);
                                        this.posActivityLog.saveLogToLocalStorage(
                                            'Product Screen',
                                            'Delete Orderline - ' + reasonPayload,
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
                                    order.remove_orderline(this.props.line);
                                    this.posActivityLog.saveLogToLocalStorage(
                                        'Product Screen',
                                        'Delete Orderline - ' + reasonPayload,
                                        this.env.pos.user.id,
                                        order.cashier.id,
                                        this.env.pos.config.id,
                                        this.env.pos.pos_session.id,
                                        order.name
                                    );
                                }
                            } else {
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Delete orderline failed!'),                    
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
                                    order.remove_orderline(this.props.line);
                                    this.posActivityLog.saveLogToLocalStorage(
                                        'Product Screen',
                                        'Delete Orderline - ' + reasonPayload,
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
                                order.remove_orderline(this.props.line);
                                this.posActivityLog.saveLogToLocalStorage(
                                    'Product Screen',
                                    'Delete Orderline - ' + reasonPayload,
                                    this.env.pos.user.id,
                                    order.cashier.id,
                                    this.env.pos.config.id,
                                    this.env.pos.pos_session.id,
                                    order.name
                                );
                            }
                        } else {
                            await this.showPopup('ErrorPopup', {
                                body: this.env._t('Delete orderline failed!'),                    
                            });
                        }
                        
                    }
                }
                // this.props.line.order.remove_orderline(this.props.line);
            }

            async clear_button_fun() {
                // this.trigger('numpad-click-input', { key: 'Backspace' });
                // this.trigger('numpad-click-input', { key: 'Backspace' });

            }

            get_total_qty_same_product() {
                const currentOrder = this.env.pos.get_order();
                if (!currentOrder) return 0;
                const selectedLine = currentOrder.get_selected_orderline();
                if (!selectedLine) return 0;
                const productId = selectedLine.product.id;
                let totalQty = 0;
                currentOrder.get_orderlines().forEach(line => {
                    if (line.product.id === productId) {
                        totalQty += line.quantity;
                    }
                });
                return totalQty;
            }

            can_be_merged_with(orderline){
                if(this.allowDelete === false){
                    return false;
                }
                return super.can_be_merged_with(...arguments);
            }

            async create_minus_one() {                
                const currentOrder = this.env.pos.get_order();
                if (currentOrder) {
                    const selectedLine = currentOrder.get_selected_orderline();                    
                    if(selectedLine.allowDelete === false){
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Error'),
                            body: this.env._t('You cannot remove this item'),
                        });
                        return;
                    }
                    const totalQty = this.get_total_qty_same_product();
                    if (totalQty > 0) {                                            
                        if (selectedLine) {
                            const { confirmed } = await this.showPopup('ConfirmPopup', {
                                title: this.env._t('Confirmation'),
                                body: this.env._t('Are you sure to reduce item ' + selectedLine.product.display_name + '?'),
                            });
                            if (confirmed) {
                                // Add new orderline with same product and quantity -1 new line don't merge                        
                                currentOrder.add_product(selectedLine.product, {quantity: -1, merge: false});
                                currentOrder.get_selected_orderline().set_allow_delete(false);
                            }
                        }
                    }else{
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Error'),
                            body: this.env._t('No items to remove'),
                        });
                    }
                }
            }

            init_from_JSON(json){
                super.init_from_JSON(...arguments);
                this.allowDelete = json.allowDelete;                
            }

            export_as_JSON(){
                var json = super.export_as_JSON();
                json.allowDelete = this.allowDelete;
                return json;
            }

            clone(){
                var orderLine = super.clone();
                orderLine.allowDelete = this.allowDelete;
                return orderLine;
            }
        };
    Registries.Component.extend(Orderline, OrderLineDelete);
    return OrderWidget;

});

