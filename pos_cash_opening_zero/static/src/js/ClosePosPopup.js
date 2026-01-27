odoo.define('pos_cash_opening_zero.ClosePosPopup', function (require) {
    "use strict";    
    const { useState, useRef, onMounted, onWillStart} = owl;
    const { _t } = require('web.core');
    const ClosePosPopup = require('point_of_sale.ClosePosPopup');
    const Registries = require("point_of_sale.Registries");
    

    const TRANSLATED_CASH_MOVE_TYPE = {
        in: _t('in'),
        out: _t('out'),
    };

    const PosCashOpeningZeroClosePosPopup = (ClosePosPopup) =>
        class extends ClosePosPopup{
            setup() {
                super.setup();
                this.closingCashInputRef = useRef('closingCashInput');
                this.tbodyDenom = useRef('tbodyDenom');
                this.state.tbodyDenomHidden = true;             
                this.state.moneyDetailsJson = [];
                this.state.cashCounts = [];
                this.cashCountsById = [];
                this.state.endCashCount = false;
                this.state.cashCounted = false;
                this.state.is_supervisor = false;
                this.state.allowPin = false;                 
                this.state.mid = false;
                this.state.end = false;
                this.popupClosed = false; // Flag to track if popup has been closed
                onWillStart(this.OnWillStart);
                onMounted(this.mounted);

                console.log('defaultCashDetails');
                console.log(this.defaultCashDetails);
                console.log('otherPaymentMethods');
                console.log(this.otherPaymentMethods);
            }

            async mounted(){
                // Check if popup was already closed by cash count process
                if (this.popupClosed) {
                    console.log('Popup already closed, skipping mount');
                    return;
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

                const data={
                    pos_session_id: this.env.pos.pos_session.id,                 
                }
                const cash_counts = await this.rpc({
                    model: 'pos.cash.count',
                    method: 'get_cash_counts',
                    args: [this.env.pos.pos_session.id],                
                }); 
                console.log('cash_counts');
                console.log(cash_counts)
                this.state.cashCounts = cash_counts                                                
                cash_counts.map((cash_count) => {
                    this.cashCountsById[cash_count.id] = cash_count;
                });                

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

            async confirm() {
                if (!this.state.endCashCount) {
                    await this.showPopup('ErrorPopup', {
                        title: this.env._t('Closing Error'),
                        body: this.env._t('Please complete end cash count before close session!')
                    });
                    return;
                }
                                                
                if (this.state.cashCounts.length == 0 ){
                    await this.showPopup('ErrorPopup', {
                        title: this.env._t('Closing Error'),    
                        body: this.env._t('Please complete cash count before close session!')
                    });  
                    return;                 
                }
                super.confirm();
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

            OnWillStart(){
                console.log('OnWillStart');
                console.log(this.env.pos.get_cashier());
                console.log(this.env.pos.res_users_supervisor_by_id[this.env.pos.get_cashier().user_id]);
                let supervisor_id = this.env.pos.res_users_supervisor_by_id[this.env.pos.get_cashier().user_id];
                if(supervisor_id != undefined){
                    this.state.is_supervisor = true;
                }else{
                    this.state.is_supervisor = false;
                }
            }

            strftimeJS(date) {
                const pad = (num) => String(num).padStart(2, '0');
                
                return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ` +
                       `${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`;
            }
            async cancel() {
                if (this.canCancel()) {
                    super.cancel();
                }
            }
            async processCashCount(employee, type){
                var self = this;
                const pos_cash_count_lines = [];
                // Cash 
                pos_cash_count_lines.push({description: this.defaultCashDetails.name ,pos_payment_method_id: this.defaultCashDetails.id, cash_count_type: 'cash', quantity: false, counted: this.state.payments[this.defaultCashDetails.id].counted, total: this.defaultCashDetails.amount, difference: this.state.payments[this.defaultCashDetails.id].difference});                            
                // Cash In Cash Out
                this.defaultCashDetails.moves.forEach((data) => {
                    console.log(data);
                    if (data.amount < 0){                            
                        pos_cash_count_lines.push({description: data.name ,pos_payment_method_id:false, cash_count_type: 'cash_out', quantity: 0, counted: data.amount, total: data.amount, difference:0});                            
                    } else {
                        pos_cash_count_lines.push({description: data.name ,pos_payment_method_id:false, cash_count_type: 'cash_in', quantity: 0, counted: data.amount, total: data.amount, difference:0});                            
                    }
                })
                // Denom                                
                console.log(this.state.moneyDetailsJson);
                this.state.moneyDetailsJson.forEach(data => {            
                    console.log(data);                                                    
                    pos_cash_count_lines.push({description: data.value ,pos_payment_method_id:false, cash_count_type: 'denomination', quantity: data.quantity || 0, counted: data.total, total: data.total, difference:0});                                                            
                })
                // Payment other than cash
                console.log(this.otherPaymentMethods);
                this.otherPaymentMethods.forEach(data => {
                    console.log(data);           
                    if (data.type == 'cash'){         
                        pos_cash_count_lines.push({
                            description: data.name ,
                            pos_payment_method_id: data.id, 
                            cash_count_type: 'cash', 
                            quantity: data.quantity || 0, 
                            counted: data.amount, 
                            total: data.amount, 
                            difference: 0});                            
                    }else{
                         pos_cash_count_lines.push({
                            description: data.name ,
                            pos_payment_method_id: data.id, 
                            cash_count_type: 'non_cash', 
                            quantity: data.quantity || 0, 
                            counted: this.state.payments[data.id].counted, 
                            total: data.amount, 
                            difference: this.state.payments[data.id].difference});   
                    }
                })

                let cashier = this.env.pos.employee_by_id[this.env.pos.get_cashier().id];
                console.log('cashier');
                console.log(this.env.pos.get_cashier());
                const data={
                    res_user_id: false,
                    hr_employee_id: this.env.pos.get_cashier().id,
                    pos_session_id: this.env.pos.pos_session.id,
                    supervisor_id: employee.id,
                    lines: pos_cash_count_lines,
                    trans_type: type,
                }
                console.log('data');
                console.log(data);
                
                await this.rpc({
                    model: 'pos.cash.count',
                    method: 'create_from_ui',
                    args: [data],
                }).then(async (response) => {
                    console.log(response);
                    console.log('Cash count created successfully, closing ClosePosPopup');
                    
                    // Close ClosePosPopup after successful save
                    self.closeClosePosPopup();
                    
                    // Generate receipt content
                    let header = `
                        <h2 style="text-align: center;">                
                            * * CASH COUNT * *
                        </h2>
                        <div style="display: flex; justify-content: space-between;">
                            <span>Store: ${this.env.pos.config.branch_code}</span>
                            <span>${this.strftimeJS(new Date())}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span>Staff: ${cashier.name}</span>
                            <span>Spv: ${employee.name}</span>
                        </div>
                        <div style="text-align: center;">-----------------------------------------------------------</div>
                    `
                    var content_detail = "";
                    pos_cash_count_lines.forEach( line => {
                        let row = `
                            <tr>
                                <td>
                                    ${line.description}
                                </td>
                                <td>
                                    ${line.quantity}
                                </td>
                                <td style="text-align: right;">
                                    ${this.env.pos.format_currency(line.total)}
                                </td>
                            </tr>
                        `
                        content_detail = content_detail + row;
                    });

                    let content = `
                        <table>
                            ${content_detail};
                        </table>
                    `;
                    let footer = '';
                    let receipt = `
                        <div style="width: 300px; margin: auto;">
                            ${header}                                                                                                                            
                            ${content}
                            ${footer}
                        </div>    
                    `;

                    // Show success message with print option
                    const countType = type === 'end' ? 'End' : 'Mid';
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Cash Count Submitted'),
                        body: this.env._t(`${countType} cash count has been recorded successfully.\n\nWould you like to print the receipt?`),
                        confirmText: this.env._t('Print Receipt'),
                        cancelText: this.env._t('Skip Print'),
                    });
                    
                    if (confirmed) {
                        // User wants to print
                        let printWindow = window.open('', '', 'width=400,height=600');
                        if (printWindow) {
                            printWindow.document.write(receipt);
                            printWindow.document.close();
                            printWindow.print();
                            
                            // Handle print completion
                            printWindow.onafterprint = function() {
                                printWindow.close();
                                self.cancel();
                                self.showLoginScreen();
                            };
                            
                            // Monitor window close
                           const checkWindowClosed = setInterval(function() {
                                if (printWindow.closed) {
                                    clearInterval(checkWindowClosed);
                                    self.cancel();
                                    self.showLoginScreen();
                                }
                            }, 500);
                        }
                    }
                    
                    // Close popup and return to login - using the same pattern as original code
                    self.cancel();
                    self.showLoginScreen();
                });
            }     

            async submitMidCashCount(){
                console.log('submitMidCashCount');
                if(!this.state.cashCounted){
                    await this.showPopup('ErrorPopup', {
                        body: this.env._t('Cash not counted yet!'),                    
                    });      
                    return true;
                }
                if (this.env.pos.config.module_pos_hr) {
                    if (!this.state.allowPin){
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
                            console.log(status);
                            if(status){           
                                await this.processCashCount(employee,'mid');      
                            }else{
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Delete orderline failed!'),                    
                                });      
                            }                            
                        }else{
                            await this.showPopup('ErrorPopup', {
                                body: this.env._t('Mid Cash Count failed!'),                    
                            });
                        }
                    }else{
                        const { payload: password } = await this.showPopup('PasswordInputPopup', {
                                title: this.env._t('Supervisor Pin?'),                    
                                isInputSelected: true,                        
                            }); 
        
                        if ( password ){
                            var supervisor = this.env.pos.res_users_supervisor_by_rfid[password];
                            const employee = this.env.pos.employee_by_user_id[supervisor.id]
                            if (supervisor) {
                                await this.processCashCount(employee,'mid');                                  
                            }else{
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Authorization Failed'),                    
                                });       
                            }
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
                            const employee = this.env.pos.employee_by_user_id[supervisor.id]
                            await this.processCashCount(employee,'mid');                               
                        }else{
                            await this.showPopup('ErrorPopup', {
                                body: this.env._t('Authorization Failed'),                    
                            });       
                        }
                    }
                }                        
            }

            async submitEndCashCount(){
                console.log('submitEndCashCount');
                if(!this.state.cashCounted){
                    await this.showPopup('ErrorPopup', {
                        body: this.env._t('Cash not counted yet!'),                    
                    });      
                    return true;
                }
                if (this.env.pos.config.module_pos_hr) {
                    if (!this.state.allowPin){
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
                            console.log(status);
                            if(status){
                                await this.processCashCount(employee,'end');
                            }else{
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('End Cash Count failed!'),                    
                                });
                            }                            
                        }else{
                            await this.showPopup('ErrorPopup', {
                                body: this.env._t('End Cash Count failed!'),                    
                            });
                        }
                        
                    }else{
                        const { payload: password } = await this.showPopup('PasswordInputPopup', {
                                title: this.env._t('Supervisor Pin?'),                    
                                isInputSelected: true,                        
                            }); 
        
                        if ( password ){
                            var supervisor = this.env.pos.res_users_supervisor_by_rfid[password];
                            const employee = this.env.pos.employee_by_user_id[supervisor.id]
                            if (supervisor) {
                                await this.processCashCount(employee,'end');     
                                // const data={
                                //     res_user_id: false,
                                //     hr_employee_id: this.env.pos.get_cashier().id,
                                //     pos_session_id: this.env.pos.pos_session.id,
                                // }
                                // console.log(data);
                                // await this.rpc({
                                //     model: 'pos.cash.count',
                                //     method: 'create_from_ui',
                                //     args: [data],
                                // }); 
                            }else{
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Authorization Failed'),                    
                                });       
                            }
                        }
                    }             
                    // const employees = []
                    // this.env.pos.res_users_supervisors
                    //     .map((supervisor) => {                  
                    //         console.log(supervisor)          
                    //         const employee = this.env.pos.employee_by_user_id[supervisor.id]
                    //         console.log(employee)
                    //         if (employee){
                    //             employees.push(
                    //                 {
                    //                     id: employee.id,
                    //                     item: employee,
                    //                     label: employee.name,
                    //                     isSelected: false,
                    //                     fingerprintPrimary: employee.fingerprint_primary,
                    //                 }
                    //             )                                                                                              
                    //         }                          
                    //     });                   

                    // let {confirmed: supervisorConfirmed, payload: employee} = await this.showPopup('SupervisorGridPopup', {
                    //         title: this.env._t('Supervisor'),
                    //         employees: employees,
                    // });
    
                    // if (supervisorConfirmed) {
                    //     if (this.state.allowPin == true){
                    //         console.log('Using pin');
                    //         if (employee && employee.pin) {
                    //             employee = await this.askPin(employee);
                    //         }

                    //         if (employee) {
                    //             await this.processCashCount(employee,'end');                                                        
                    //         }
                    //     } else {
                    //         var { confirmed: fingerConfirmed } = await this.showPopup('FingerprintAuthPopup', {employee: employee});
                    //         console.log(fingerConfirmed);
                    //         console.log(this.state.payments);
                    //         if(fingerConfirmed){                                
                    //             await this.processCashCount(employee,'end');                                                        
                    //         }else{
                    //             await this.showPopup('ErrorPopup', {
                    //                 body: this.env._t('Cash process failed!'),                    
                    //             });      
                    //         }
                    //     }
                    // }
                }else{                
                    const { payload: password } = await this.showPopup('PasswordInputPopup', {
                                title: this.env._t('Supervisor Pin?'),                    
                                isInputSelected: true,                        
                            }); 
        
                    if ( password ){
                        var supervisor = this.env.pos.res_users_supervisor_by_rfid[password];
                        const employee = this.env.pos.employee_by_user_id[supervisor.id]
                        if (supervisor) {
                            await this.processCashCount(employee,'end');    
                            // const data={
                            //     res_user_id: false,
                            //     hr_employee_id: this.env.pos.get_cashier().id,
                            //     pos_session_id: this.env.pos.pos_session.id,
                            // }
                            // console.log(data);
                            // await this.rpc({
                            //     model: 'pos.cash.count',
                            //     method: 'create_from_ui',
                            //     args: [data],
                            // }); 
                        }else{
                            await this.showPopup('ErrorPopup', {
                                body: this.env._t('Authorization Failed'),                    
                            });       
                        }
                    }
                }           
            }

            updateCountedCash({ total, moneyDetailsNotes, moneyDetails }) {
                this.closingCashInputRef.el.value = this.env.pos.format_currency_no_symbol(total);
                this.state.payments[this.defaultCashDetails.id].counted = total;
                this.state.payments[this.defaultCashDetails.id].difference =
                    this.env.pos.round_decimals_currency(this.state.payments[[this.defaultCashDetails.id]].counted - this.defaultCashDetails.amount);
                if (moneyDetailsNotes) {
                    this.state.notes = moneyDetailsNotes;
                }
                this.manualInputCashCount = false;
                this.moneyDetails = moneyDetails;
                this.env.pos.bills.forEach(bill => {
                    if (moneyDetails[bill.value]) {
                        this.state.moneyDetailsJson.push({quantity: moneyDetails[bill.value], value: bill.value, fmtAmount: this.env.pos.format_currency(bill.value), total: bill.value * moneyDetails[bill.value], fmtTotal:this.env.pos.format_currency(bill.value * moneyDetails[bill.value])});                        
                    }else{
                        this.state.moneyDetailsJson.push({quantity: 0, value: bill.value, fmtAmount: this.env.pos.format_currency(bill.value), total: 0, fmtTotal:this.env.pos.format_currency(0) });                        
                    }
                });
                this.state.tbodyDenomHidden = false;
                this.state.cashCounted = true;
                this.closeDetailsPopup();
            }

            async closeSession() {                                     
                const reason = "";
                const type = "out";
                const amount = -1 * this.state.payments[this.defaultCashDetails.id].difference;
                this.state.payments[this.defaultCashDetails.id].difference = 0;
                const translatedType = TRANSLATED_CASH_MOVE_TYPE['out'];
                const formattedAmount = this.env.pos.format_currency(amount);                
                const extras = { formattedAmount, translatedType };
                await this.rpc({
                    model: 'pos.session',
                    method: 'try_cash_in_out',
                    args: [[this.env.pos.pos_session.id], type, amount, reason, extras],
                }).then(response => {
                    const pos_cash_count_lines = [];
                    pos_cash_count_lines.push({description: this.defaultCashDetails.name ,quantity: false, total: this.defaultCashDetails.amount, counted: this.defaultCashDetails.counted});                                            

                    console.log(this.state.moneyDetailsJson);
                    this.state.moneyDetailsJson.forEach(data => {
                        pos_cash_count_lines.push({description: data.value ,quantity: data.quantity || 0, total: data.total});                            
                    })
                    console.log(this.otherPaymentMethods);
                    this.otherPaymentMethods.forEach(data => {
                        pos_cash_count_lines.push({description: data.name ,quantity: data.quantity || 0, total: data.amount});                            
                    })
                    const data={
                        res_user_id: false,
                        hr_employee_id: this.env.pos.get_cashier().id,
                        pos_session_id: this.env.pos.pos_session.id,
                        lines: pos_cash_count_lines,
                    }
                    console.log(data);
                });
                super.closeSession();
            }
            
            async onPrintClick(ev){
                const id = ev.currentTarget.dataset.id;
                console.log('id');
                console.log(id);
                let cash_count = this.cashCountsById[id];                                
                let header = `
                    <h2 style="text-align: center;">                
                        * * CASH COUNT 2 * *
                    </h2>
                        <div style="display: flex; justify-content: space-between;">
                        <span>Store: ${this.env.pos.config.branch_code}</span>
                        <span>${cash_count.name}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Staff: ${cash_count.cashier[1]}</span>
                        <span>Spv: ${cash_count.supervisor[1]}</span>
                    </div>
                    <div style="text-align: center;">---------------------------------------------------------</div>
                `
                var content_detail = "";
                cash_count.details.forEach( line => {
                    let row = `
                        <tr>
                            <td>
                                ${line.description}
                            </td>
                            <td>
                                ${line.quantity}
                            </td>
                            <td style="text-align: right;">
                                ${this.env.pos.format_currency(line.total)}
                            </td>
                        </tr>
                    `
                    content_detail = content_detail + row;
                });

                let content = `
                    <table>
                        ${content_detail};
                    </table>
                `;
                let footer = '';
                let receipt = `
                    <div style="width: 300px; margin: auto;">
                        ${header}                                                                                                                            
                        ${content}
                        ${footer}
                    </div>    
                `;
                let printWindow = window.open('', '', 'width=400,height=600');
                printWindow.document.write(receipt);
                printWindow.document.close();
                printWindow.print();                                                                                
            }

            async showFinalConfirmation(type) {
                console.log('showFinalConfirmation called for type:', type);
                // Skip showing confirmation popup since ClosePosPopup is already closed
                // Just return to login screen directly
                await this.returnToLogin();
            }

            closeClosePosPopup() {
                console.log('Closing ClosePosPopup - attempting all methods');
                
                // Set flag to prevent re-rendering
                this.popupClosed = true;
                
                try {
                    // Method 1: Cancel like the confirm button does
                    console.log('Method 1: Using cancel');
                    this.cancel();
                    return;
                } catch (e) {
                    console.log('Method 1 failed:', e);
                }
                
                try {
                    // Method 2: Try to reject the popup promise
                    if (this.props && this.props.reject) {
                        console.log('Method 2: Rejecting via props.reject');
                        this.props.reject();
                        return;
                    }
                } catch (e) {
                    console.log('Method 2 failed:', e);
                }
                
                try {
                    // Method 3: Try to resolve the popup promise
                    if (this.props && this.props.resolve) {
                        console.log('Method 3: Resolving via props.resolve');
                        this.props.resolve({ confirmed: false, payload: null });
                        return;
                    }
                } catch (e) {
                    console.log('Method 3 failed:', e);
                }
            }

            async returnToLogin() {
                console.log('returnToLogin called');
                console.log('Current cashier:', this.env.pos.get_cashier());
                
                try {
                    // Reset cashier
                    this.env.pos.reset_cashier();
                    console.log('Cashier reset completed');
                    
                    // Show login screen using the POS chrome component
                    console.log('Attempting to show LoginScreen...');
                    
                    // Get the chrome component from the POS
                    const chrome = this.env.pos.chrome || this.chrome;
                    if (chrome && chrome.showTempScreen) {
                        await chrome.showTempScreen('LoginScreen');
                        console.log('LoginScreen shown via chrome');
                    } else if (this.showTempScreen) {
                        await this.showTempScreen('LoginScreen');
                        console.log('LoginScreen shown via this.showTempScreen');
                    } else {
                        // Direct manipulation of the screen
                        console.log('Using direct screen manipulation');
                        this.env.pos.set('tempScreen', { name: 'LoginScreen' });
                    }
                    
                    console.log('LoginScreen shown successfully');
                } catch (error) {
                    console.log('Error in returnToLogin:', error);
                    console.log('Error stack:', error.stack);
                }
            }

            async showLoginScreen() {
                this.env.pos.reset_cashier();
                await this.showTempScreen('LoginScreen');
            }
        }

    Registries.Component.extend(ClosePosPopup, PosCashOpeningZeroClosePosPopup);
    return PosCashOpeningZeroClosePosPopup;
});