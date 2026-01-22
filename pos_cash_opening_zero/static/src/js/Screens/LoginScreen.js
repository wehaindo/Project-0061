odoo.define('pos_cash_opening_zero.LoginScreen', function (require) {
    'use strict';

    const LoginScreen = require('pos_hr.LoginScreen');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, useState } = owl;
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');

    const OpeningZeroLoginScreen = (LoginScreen) => 
        class extends LoginScreen {
            setup(){
                super.setup();                
                this.state.endCashCount = false;
                this.posActivityLog = new PosActivityLog();
                onMounted(this.mounted);
            }

            async mounted(){
                super.mounted();
                const end_cash_count = await this.rpc({
                    model: 'pos.cash.count',
                    method: 'check_end_cash_count',  
                    args: [this.env.pos.pos_session.id],
                }); 

                if(end_cash_count === true){
                    this.state.endCashCount = true;
                } else {
                    this.state.endCashCount = false;
                }
            }

            async selectEmployee() {
                console.log("Select Employee 1");
                console.log("End Cash Count:", this.state.endCashCount);
                if (this.env.pos.config.module_pos_hr) {
                    const employees = this.env.pos.employees
                        .filter((employee) => employee.id !== this.env.pos.get_cashier().id)
                        .map((employee) => {
                            return {
                                id: employee.id,
                                item: employee,
                                label: employee.name,
                                isSelected: false,
                                fingerprintPrimary: employee.fingerprint_primary,
                            };
                        });
                    

                    let {confirmed, payload: employee} = await this.showPopup('EmployeeGridPopup', {
                        title: this.env._t('Change Cashier'),
                        employees: employees,
                    });

                    //Check Employee is Supervisor
                    if(this.state.endCashCount){
                        console.log("Check Supervisor");
                        console.log("Supervisor List:", this.env.pos.res_users_supervisors);
                        console.log("Employee User ID:", employee.user_id[0]);
                        if(!this.env.pos.res_users_supervisors.find(supervisor => supervisor.id === employee.user_id)){
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Cashier cannot login because end cash count is completed'),
                                body: this.env._t('Cash count has been completed. Please contact your manager.'),
                            });
                            return;
                        }                        
                    }

                    if (confirmed) {
                        var { confirmed: fingerConfirmed } = await this.showPopup('FingerprintAuthPopup', {employee: employee});
                        console.log(fingerConfirmed);
                        if (fingerConfirmed) {
                            if (employee) {
                                this.env.pos.set_cashier(employee); 
                                this.posActivityLog.saveLogToLocalStorage(
                                    'Login Screen',
                                    'User Login',
                                    this.env.pos.user.id,
                                    employee.id,
                                    this.env.pos.config.id,
                                    this.env.pos.pos_session.id,
                                    employee.name
                                );
                                this.back();                                                  
                            }
                            return;
                        }else{
                            return;
                        }
                    }                   
                    // if (employee && employee.pin) {
                    //     employee = await this.askPin(employee);
                    // }
                                   
                }
            }

            async selectCashier() {                
                console.log("pos_cash_opening_zero  : Select Cashier");   
                console.log("End Cash Count:", this.state.endCashCount);             
                if (this.env.pos.config.module_pos_hr) {
                    const employees = this.env.pos.employees
                        .filter((employee) => employee.id !== this.env.pos.get_cashier().id)
                        .map((employee) => {
                            return {
                                id: employee.id,
                                item: employee,
                                label: employee.name,
                                isSelected: false,
                                fingerprintPrimary: employee.fingerprint_primary,
                            };
                        });
    
                    let {confirmed, payload: employee} = await this.showPopup('EmployeeGridPopup', {
                        title: this.env._t('Change Cashier'),
                        employees: employees,
                    });

                    //Check Employee is Supervisor
                    if(this.state.endCashCount){
                        console.log("Check Supervisor");
                        console.log("Supervisor List:", this.env.pos.res_users_supervisors);
                        console.log("Employee User ID:", employee);
                        if(!this.env.pos.res_users_supervisors.find(supervisor => supervisor.id === employee.user_id)){ 
                            this.showPopup('ErrorPopup', {
                                title: this.env._t('Login Prohibited'),                        
                                body: this.env._t('Cash count has been completed. Please contact your manager.'),
                            });
                            return;
                        }                        
                    }
    
                    if (!confirmed) {
                        return;
                    }

                    if (employee && employee.pin) {
                        employee = await this.askPin(employee);
                    }

                    if (employee) {
                        this.env.pos.set_cashier(employee);
                        this.back();                            
                    }                    
                }

               
                // await super.selectCashier();
             }
        }
    
    Registries.Component.extend(LoginScreen, OpeningZeroLoginScreen);
    
})