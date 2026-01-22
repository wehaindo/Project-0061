odoo.define('weha_smart_pos_disable_refund.ReprintReceiptButton', function (require) {
    'use strict';

    const { onMounted, useRef, useState } = owl;
    const Registries = require('point_of_sale.Registries');
    const ReprintReceiptButton = require('point_of_sale.ReprintReceiptButton');
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');

    const DisableRefundReprintReceiptButton = (ReprintReceiptButton) =>
        class extends ReprintReceiptButton {
            setup() {
                super.setup();
                this.posActivityLog = new PosActivityLog();
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
        

            async _onClick() {
                const { payload: reasonPayload } = await this.showPopup('TextInputPopup',{
                    title: this.env._t('Print Receipt Reason'),
                    body: 'Please input print receipt reason!',
                });   
            

                if(reasonPayload){
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
                                if (!this.props.order) return;                    
                                this.posActivityLog.saveLogToLocalStorage(
                                    'Ticket Screen',
                                    'Reprint Receipt - ' + this.props.order.name,
                                    this.env.pos.user.id,
                                    this.props.order.cashier.id,
                                    this.env.pos.config.id,
                                    this.env.pos.pos_session.id,
                                    this.props.order.name
                                );
                                this.showScreen('ReprintReceiptScreen', { order: this.props.order,  printType: 'reprint' });                                
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
                                if (!this.props.order) return;                    
                                    this.posActivityLog.saveLogToLocalStorage(
                                        'Ticket Screen',
                                        'Reprint Receipt - ' + reasonPayload,
                                        this.env.pos.user.id,
                                        this.props.order.cashier.id,
                                        this.env.pos.config.id,
                                        this.env.pos.pos_session.id,
                                        this.props.order.name
                                    );
                                    this.showScreen('ReprintReceiptScreen', { order: this.props.order , printType: 'reprint' });
                            }else{
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Reprint transaction failed!'),                    
                                });       
                            }
                        }                                   
                    }                        
                }
            }
        }

    Registries.Component.extend(ReprintReceiptButton, DisableRefundReprintReceiptButton);
});
