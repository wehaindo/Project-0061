odoo.define('pos_cash_opening_zero.CashMoveButton', function (require) {
    'use strict';

    const { useState, useRef, onMounted } = owl;
    const CashMoveButton = require('point_of_sale.CashMoveButton');
    const Registries = require("point_of_sale.Registries");
    const { _t } = require('web.core');
    const { renderToString } = require('@web/core/utils/render');
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');
    const { isConnectionError } = require('point_of_sale.utils');


    const TRANSLATED_CASH_MOVE_TYPE = {
        in: _t('in'),
        out: _t('out'),
    };

    const PosCashOpeningZeroCashMoveButton = (CashMoveButton) => 
        class extends CashMoveButton {
            setup() {
                super.setup();
                this.state = useState({allowPin:false});
                this.posActivityLog = new PosActivityLog();
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

            async askPin(employee) {
                const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                    isPassword: true,
                    title: this.env._t('Password ?'),
                    startingValue: null,
                });

                if (!confirmed) return;

                if (employee.pin === Sha1.hash(inputPin)) {
                    return employee;
                } else {
                    await this.showPopup('ErrorPopup', {
                        title: this.env._t('Incorrect Password'),
                    });
                    return;
                }
            }

            strftimeJS(date) {
                const pad = (num) => String(num).padStart(2, '0');                
                return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ` +
                       `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
            }

            async onClick() {
                console.log('PosCashOpeningZeroCashMoveButton - onClick');                
                const { confirmed, payload } = await this.showPopup('CashMovePopup');
                if (!confirmed) return;                  
                
                try {                     
                    const payloadData = payload;                       
                    if (this.env.pos.config.module_pos_hr) {     
                        if (!this.state.allowPin) {
                            const employees = []
                            this.env.pos.res_users_supervisors
                                    .map((supervisor) => {                  
                                        console.log(supervisor)          
                                        const employee = this.env.pos.employee_by_user_id[supervisor.id]
                                        console.log(employee)
                                        if (employee){
                                            employees.push(
                                                {
                                                    id: employee.id,
                                                    item: employee,
                                                    label: employee.name,
                                                    isSelected: false,
                                                    fingerprintPrimary: employee.fingerprint_primary,
                                                }
                                            )                                                                                              
                                        }                          
                                    });                                

                            let {confirmed: supervisorConfirmed, payload: employee} = await this.showPopup('SupervisorGridPopup', {
                                title: this.env._t('Supervisor'),
                                employees: employees,
                            });                      

                            if (supervisorConfirmed && employee) {     
                                var { payload: status } = await this.showPopup('FingerprintAuthPopup', {employee: employee});                                
                                if(status){   
                                    const { type, amount, reason, details } = payloadData;
                                    const translatedType = TRANSLATED_CASH_MOVE_TYPE[type];
                                    const formattedAmount = this.env.pos.format_currency(amount);
                                    if (!amount) {
                                        return this.showNotification(
                                            _.str.sprintf(this.env._t('Cash in/out of %s is ignored.'), formattedAmount),
                                            3000
                                        );
                                    }
                                    const extras = { formattedAmount, translatedType };
                                    await this.rpc({
                                        model: 'pos.session',
                                        method: 'try_cash_in_out',
                                        args: [[this.env.pos.pos_session.id], type, amount, reason, extras],
                                    });
                                    if (this.env.proxy.printer) {
                                        const renderedReceipt = renderToString('point_of_sale.CashMoveReceipt', {
                                            _receipt: this._getReceiptInfo({ ...payloadData, translatedType, formattedAmount }),
                                        });
                                        const printResult = await this.env.proxy.printer.print_receipt(renderedReceipt);
                                        if (!printResult.successful) {
                                            this.showPopup('ErrorPopup', { title: printResult.message.title, body: printResult.message.body });
                                        }
                                    }else{
                                        console.log("Print Cash In Out Receipt"); 
                                        const receipt_data = {
                                            header: "* * LOAN * *",       
                                            type: type,
                                            amount: amount,
                                            reason: reason,
                                            date: this.strftimeJS(new Date()),
                                            cashier: this.env.pos.get_cashier(),
                                            supervisor: employee,
                                            details: details                   
                                        }
                                        this.showScreen('CashInOutReceiptScreen', { reuseSavedUIState: true , data: receipt_data});
                                    }
                                    this.showNotification(
                                        _.str.sprintf(this.env._t('Successfully made a cash %s of %s.'), type, formattedAmount),
                                        3000
                                    );
                                }else{
                                    await this.showPopup('ErrorPopup', { title: this.env._t('Error'), body: this.env._t('Fingerprint authentication failed.') });
                                }                                
                            }else{
                                await this.showPopup('ErrorPopup', { title: this.env._t('Error'), body: this.env._t('Please select a supervisor.') });
                            }                                
                        }else{                            
                            const { payload: password } = await this.showPopup('PasswordInputPopup', {
                                title: this.env._t('Supervisor Pin?'),                    
                                isInputSelected: true,                        
                            }); 
                            if ( password ){
                                var supervisor = this.env.pos.res_users_supervisor_by_rfid[password];                                
                                if (supervisor) { 
                                    // await this.activatePin();
                                    const employee = this.env.pos.employee_by_user_id[supervisor.id]
                                    const { type, amount, reason, details } = payloadData;
                                    const translatedType = TRANSLATED_CASH_MOVE_TYPE[type];
                                    const formattedAmount = this.env.pos.format_currency(amount);
                                    if (!amount) {
                                        return this.showNotification(
                                            _.str.sprintf(this.env._t('Cash in/out of %s is ignored.'), formattedAmount),
                                            3000
                                        );
                                    }
                                    const extras = { formattedAmount, translatedType };
                                    await this.rpc({
                                        model: 'pos.session',
                                        method: 'try_cash_in_out',
                                        args: [[this.env.pos.pos_session.id], type, amount, reason, extras],
                                    });
                                    if (this.env.proxy.printer) {
                                        const renderedReceipt = renderToString('point_of_sale.CashMoveReceipt', {
                                            _receipt: this._getReceiptInfo({ ...payloadData, translatedType, formattedAmount }),
                                        });
                                        const printResult = await this.env.proxy.printer.print_receipt(renderedReceipt);
                                        if (!printResult.successful) {
                                            this.showPopup('ErrorPopup', { title: printResult.message.title, body: printResult.message.body });
                                        }
                                    }else{
                                        console.log("Print Cash In Out Receipt"); 
                                        const receipt_data = {
                                            header: "* * LOAN * *",       
                                            type: type,
                                            amount: amount,
                                            reason: reason,
                                            date: this.strftimeJS(new Date()),
                                            cashier: this.env.pos.get_cashier(),
                                            supervisor: employee,
                                            details: details                   
                                        }
                                        console.log('receipt_data');
                                        console.log(receipt_data);
                                        this.showScreen('CashInOutReceiptScreen', { reuseSavedUIState: true , data: receipt_data});
                                    }
                                    this.showNotification(
                                        _.str.sprintf(this.env._t('Successfully made a cash %s of %s.'), type, formattedAmount),
                                        3000
                                    );
                                }else{
                                    await this.showPopup('ErrorPopup', {title: this.env._t('Error'), body: this.env._t('Supervisor not found.') });
                                }
                            }
                        }                                           
                    }else{                
                        const { confirmed, payload } = await this.showPopup('PasswordInputPopup', {
                            title: this.env._t('Supervisor Pin?'),                    
                            isInputSelected: true,                        
                        }); 
    
                        if ( confirmed ){
                            var supervisor = this.env.pos.res_users_supervisor_by_rfid[payload];
                            if (supervisor) {
                                // this.posActivityLog.saveLogToLocalStorage('Ticket Screen','Void Transaction',order.cashier.id);
                                const employee = this.env.pos.employee_by_user_id[supervisor.id]
                                console.log('Supervisor Valid');
                                const { type, amount, reason } = payloadData;
                                console.log(payload);
                                const translatedType = TRANSLATED_CASH_MOVE_TYPE[type];
                                const formattedAmount = this.env.pos.format_currency(amount);
                                if (!amount) {
                                    return this.showNotification(
                                        _.str.sprintf(this.env._t('Cash in/out of %s is ignored.'), formattedAmount),
                                        3000
                                    );
                                }
                                const extras = { formattedAmount, translatedType };
                                console.log('start try_cash_in_out');
                                await this.rpc({
                                    model: 'pos.session',
                                    method: 'try_cash_in_out',
                                    args: [[this.env.pos.pos_session.id], type, amount, reason, extras],
                                });
                                if (this.env.proxy.printer) {
                                    const renderedReceipt = renderToString('point_of_sale.CashMoveReceipt', {
                                        _receipt: this._getReceiptInfo({ ...payload, translatedType, formattedAmount }),
                                    });
                                    const printResult = await this.env.proxy.printer.print_receipt(renderedReceipt);
                                    if (!printResult.successful) {
                                        this.showPopup('ErrorPopup', { title: printResult.message.title, body: printResult.message.body });
                                    }
                                }else{
                                    console.log("Print Cash In Out Receipt"); 
                                    this.showScreen('CashInOutReceiptScreen', { reuseSavedUIState: true });
                                }
                                this.showNotification(
                                    _.str.sprintf(this.env._t('Successfully made a cash %s of %s.'), type, formattedAmount),
                                    3000
                                );
                            }else{
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Authorization Failed'),                    
                                });       
                            }
                        }    
                    }            
                } catch (error) {
                    console.log(error);
                    if (isConnectionError(error)) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Network Error'),
                            body: this.env._t('Unable to void order.'),
                        });
                    } else {
                        throw error;
                    }
                } finally {                    
                }          
                
            }
        }
    
    Registries.Component.extend(CashMoveButton, PosCashOpeningZeroCashMoveButton);
    return PosCashOpeningZeroCashMoveButton
});