odoo.define('weha_smart_pos_disable_refund.VoidButton', function (require) {
    'use strict';

    const { onMounted, useRef, useState } = owl;
    const { useListener } = require("@web/core/utils/hooks");    
    const { isConnectionError } = require('point_of_sale.utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    // const FingerprintAuthPopup  = require('weha_smart_pos_aeon_pos_access_rights.FingerprintAuthPopup');
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');

    class VoidButton extends PosComponent {
        setup() {
            super.setup();
            this.posActivityLog = new PosActivityLog();
            this.state = useState({allowPin:false});
            onMounted(this.mounted);
            // this.FingerprintAuthPopup = new FingerprintAuthPopup();
            useListener('click', this._onClick);
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
    

        get commandName() {
            return this.env._t('Refund All');
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
                refunded_qty: line.quantity,
                price_source: line.price_source
            }
            return options;
        }

        async add_orderlines(order, void_order){
            console.log("add_orderlines");
            for (const line of order.orderlines) {          
                console.log(line);      
                const product = this.env.pos.db.get_product_by_id(line.product.id);                
                const options = this.set_options(line);   
                console.log(options);
                // await void_order.add_product(product, options);

                // Complete Void Orderline
                var new_line = line.clone();                
                new_line.quantity = line.quantity * -1
                new_line.refunded_orderline_id = line.id
                new_line.merge = false
                new_line.refunded_qty =  line.quantity
                new_line.price_manually_set = true
                new_line.price_override_user = false

                await void_order.add_orderline(new_line);
            }
        }

        async add_payments(order, void_order){
            console.log('weha_smart_pos_disable_refund.VoidButton.add_payment');            
        }

        getOrderRefundStatus(order) {
            if (!order) return { hasRefund: false, isFullRefund: false, isPartialRefund: false };
            
            // Check if this order itself is a refund or void
            if (order.is_refund || order.is_void) {
                return {
                    hasRefund: false,
                    isFullRefund: false,
                    isPartialRefund: false,
                    isRefundOrder: true,
                    message: 'This is a refund or void order'
                };
            }
            
            // Get all order lines from the original order
            const orderLines = order.orderlines || [];
            console.log('orderLines', orderLines);
            const totalOrderQty = orderLines.reduce((sum, line) => sum + Math.abs(line.quantity), 0);
            
            // Get refunded quantities for this order
            const refundedQty = orderLines.reduce((sum, line) => sum + Math.abs(line.refunded_qty), 0);

            // Determine refund status
            const hasRefund = refundedQty > 0;
            const isFullRefund = hasRefund && this.env.pos.isProductQtyZero(totalOrderQty - refundedQty);
            const isPartialRefund = hasRefund && !isFullRefund;
            
            return {
                hasRefund,
                isFullRefund,
                isPartialRefund,
                totalOrderQty,
                refundedQty,
                remainingQty: totalOrderQty - refundedQty,
                isRefundOrder: false
            };
        }

        async _voidOrder() {            
            console.log("order void")
            var order = this.props.order;
            console.log("order refund")
            console.log(order);            
            if (!order) return;
            const void_order = this.env.pos.add_new_order();
            this.init_data(order, void_order);
            await this.add_orderlines(order, void_order);
            void_order.set_is_void(true);
            void_order.set_void_parent_pos_reference(order.name);
            await this.add_payments(order,void_order);
            this.env.pos.set_order(void_order);
            this.showScreen('ProductScreen');              
        }        

       

        async _onClick() {
            try {
                this.el.style.pointerEvents = 'none';
                var order = this.props.order;
                if (order.is_refund || order.is_void) {
                    await this.showPopup('ErrorPopup', {
                        body: this.env._t('This order has been voided already!'),
                    });
                    return;
                }                
                const {  
                    hasRefund,
                    isFullRefund,
                    isPartialRefund,
                    totalOrderQty,
                    refundedQty,
                    remainingQty,
                    isRefundOrder 
                } = this.getOrderRefundStatus(order);

                console.log('isFullRefund');
                console.log(isFullRefund);
                console.log('isPartialRefund');
                console.log(isPartialRefund);

                if (isFullRefund) {
                    await this.showPopup('ErrorPopup', {          
                        title: this.env._t('Order Refund All'),
                        body: this.env._t('This order has already been fully refunded and cannot be Refunded All.')
                    });
                    return;
                }
                if (isPartialRefund) {
                    await this.showPopup('ErrorPopup', {          
                        title: this.env._t('Order Partial Refund'),
                        body: this.env._t('This order has been partially refunded and cannot be Refunded All. Please use the Refund Selected function.')
                    });
                    return;
                }
                const { confirmed,  payload: reasonPayload } = await this.showPopup('TextInputPopup',{
                        title: this.env._t('Refund Reason'),
                        body: 'Please input refund reason!',
                    });   

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
                            var { payload: status } = await this.showPopup('FingerprintAuthPopup', {employee: employee});
                            console.log(status);
                            if(status){
                                this.posActivityLog.saveLogToLocalStorage(
                                    'Ticket Screen',
                                    'Void Transaction - ' + status,
                                    this.env.pos.user.id,
                                    order.cashier.id,
                                    this.env.pos.config.id,
                                    this.env.pos.pos_session.id,
                                    order.name
                                );                                
                                await this._voidOrder();
                            }else{
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Void transaction failed!'),                    
                                });      
                            }
                        }                        
                    }else{                                        
                        const { payload: password } = await this.showPopup('PasswordInputPopup', {
                            title: this.env._t('Supervisor Pin?'),                    
                            isInputSelected: true,                        
                        }); 

                        if ( password ){
                            var supervisor = this.env.pos.res_users_supervisor_by_rfid[password];
                            if (supervisor) {
                                this.posActivityLog.saveLogToLocalStorage('Ticket Screen','Void Transaction',order.cashier.id);
                                await this._voidOrder();
                            }else{
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Void transaction failed!'),                    
                                });       
                            }
                        }
                                        
                    }        
                }else{
                    this.showPopup('ErrorPopup', {
                        title: this.env._t('Void Error'),
                        body: this.env._t('Void reason is required.'),
                    });                    
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