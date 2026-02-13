odoo.define('weha_smart_pos_aeon_pos_access_rights.LoginScreen', function (require) {
    'use strict';

    const LoginScreen = require('pos_hr.LoginScreen');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, useState } = owl;
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');



    const PosAccessRightsLoginScreen = (LoginScreen) => 
        class extends LoginScreen {
            setup(){
                super.setup();
                this.state = useState({allowPin:false});
                this.posActivityLog = new PosActivityLog();
                onMounted(this.mounted);
            }

            mounted(){
                console.log('getItem - allowPin');
                console.log(localStorage.getItem('allowPin'));           
                let allowPin = localStorage.getItem('allowPin');
                let savedDate = localStorage.getItem('allowPinDate');
                let currentDate = new Date().toDateString();
                                
                if (Boolean(allowPin) === true && savedDate === currentDate) {
                    console.log('set state allowpin')
                    this.state.allowPin = true;     
                } else if (Boolean(allowPin) === true && savedDate !== currentDate) {
                    // Different date, reset allowPin
                    console.log('Different date detected, resetting allowPin');
                    localStorage.setItem('allowPin', 'false');
                    localStorage.removeItem('allowPinDate');
                    this.state.allowPin = false;
                }
            }

            async disablePin(){
                localStorage.setItem('allowPin', 'false');
                localStorage.removeItem('allowPinDate');
                this.state.allowPin = false;
                
                // Log activity when PIN is deactivated
                const currentEmployee = this.env.pos.get_cashier();
                if (currentEmployee) {
                    this.posActivityLog.saveLogToLocalStorage(
                        'Login Screen',
                        'PIN Deactivated (Switched to Fingerprint)',
                        this.env.pos.user.id,
                        currentEmployee.id,
                        this.env.pos.config.id,
                        this.env.pos.pos_session.id,
                        currentEmployee.name
                    );
                }
            }   

            async selectSupervisor() {
                console.log("Select Supervisor");
                console.log(this.env.pos.res_users_supervisors)
                const employees = []
                this.env.pos.res_users_supervisors
                        // .filter((supervisor) => this.env.pos.employee_by_user_id[supervisor.id])
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

                console.log(employees);
                // const supervisors = this.env.pos.res_users_supervisors
                //     .map((supervisor) => {
                //         return {
                //             id: supervisor.id,
                //             item: supervisor,
                //             label: supervisor.name,
                //             isSelected: false,
                //         };
                //     })
                
                  let {confirmed, payload: employee} = await this.showPopup('SupervisorGridPopup', {
                        title: this.env._t('Supervisor'),
                        employees: employees,
                    });
    
                    if (confirmed) {
                        console.log(confirmed);
                        console.log(employee);
                        // const { confirmed:confirmedPin, payload: inputPin } = await this.showPopup('NumberPopup', {
                        //     isPassword: true,
                        //     title: this.env._t('Password ?'),
                        //     startingValue: null,
                        // });

                        // console.log(confirmedPin);
                        // console.log(inputPin);

                        // if (!confirmed) {
                        //     return;
                        // }

                        if (employee && employee.pin) {
                            const { confirmed: pinConfirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                                isPassword: true,
                                title: this.env._t('Password ?'),
                                startingValue: null,
                            });
                            
                            console.log(pinConfirmed);
                            console.log(inputPin);
                            
                            // Check if PIN was cancelled
                            if (!pinConfirmed) {
                                return;
                            }
                            
                            // Verify the PIN matches
                            if (employee.pin !== inputPin) {
                                await this.showPopup('ErrorPopup', {
                                    title: this.env._t('Incorrect PIN'),
                                    body: this.env._t('The PIN you entered is incorrect. Please try again.'),
                                });
                                return;
                            }
                        }

                        if (employee) {
                            await this.activatePin();
                        }                                                      
                    }
            }

            async selectEmployee() {
                console.log("Select Employee 1");
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
                    
                    // let {confirmed, payload: employee} = await this.showPopup('SelectionPopup', {
                    //     title: this.env._t('Change Cashier'),
                    //     list: employees,
                    // });

                    let {confirmed, payload: employee} = await this.showPopup('EmployeeGridPopup', {
                        title: this.env._t('Change Cashier'),
                        employees: employees,
                    });
    
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
                console.log("Select Cashier 1");
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
            }

            async activatePin(){
                let currentDate = new Date().toDateString();
                localStorage.setItem('allowPin','true');
                localStorage.setItem('allowPinDate', currentDate);
                this.state.allowPin = true;
                
                // Log activity when PIN is activated
                const currentEmployee = this.env.pos.get_cashier();
                if (currentEmployee) {
                    this.posActivityLog.saveLogToLocalStorage(
                        'Login Screen',
                        'PIN Activated',
                        this.env.pos.user.id,
                        currentEmployee.id,
                        this.env.pos.config.id,
                        this.env.pos.pos_session.id,
                        currentEmployee.name
                    );
                }
            }
           
        }       

    Registries.Component.extend(LoginScreen, PosAccessRightsLoginScreen);        
});