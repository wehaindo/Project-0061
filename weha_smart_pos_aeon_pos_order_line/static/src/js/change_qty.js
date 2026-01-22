odoo.define('weha_smart_pos_aeon_pos_order_line.ChangeQtyOrderline', function(require) {
'use strict';
   const { useState, useRef, onPatched, onMounted } = owl;   
   const PosComponent = require('point_of_sale.PosComponent');   
   const ProductScreen = require('point_of_sale.ProductScreen');
   const { useListener } = require("@web/core/utils/hooks");
   const Registries = require('point_of_sale.Registries');
   const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');

   class OrderLineChangeQty extends PosComponent {
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
    
                 
    //    async onClick() {
    //         if (this.env.pos.config.module_pos_hr) {
    //             const {payload: reasonPayload} = await this.showPopup("NumberPopup", {
    //                    title: this.env._t('Change QTY?'),
    //             });
            
    //             if(reasonPayload){
    //                 if (!this.state.allowPin){
    //                     const employees = this.env.pos.res_users_supervisors
    //                     .filter((supervisor) => this.env.pos.employee_by_user_id[supervisor.id])
    //                     .map((supervisor) => {
    //                         const employee = this.env.pos.employee_by_user_id[supervisor.id]
    //                         return {
    //                             id: employee.id,
    //                             item: employee,
    //                             label: employee.name,
    //                             isSelected: false,
    //                             fingerprintPrimary: employee.fingerprint_primary,
    //                         };
    //                     });

    //                     let {payload: employee} = await this.showPopup('SelectionPopup', {
    //                         title: this.env._t('Select Supervisor'),
    //                         body: "Change QTY to " + reasonPayload,
    //                         list: employees,
    //                     });
        
    //                     if (employee) {
    //                         var { payload: status } = await this.showPopup('FingerprintAuthPopup', {employee: employee});
    //                         console.log(status);
    //                         if(status){                                                                                
    //                             var order    = this.env.pos.get_order();
    //                             var line  = order.get_selected_orderline();
    //                             line.set_quantity(reasonPayload);
    //                             this.posActivityLog.saveLogToLocalStorage(
    //                                 'Product Screen',
    //                                 'Change QTY',
    //                                 this.env.pos.user.id,
    //                                 order.cashier.id,
    //                                 this.env.pos.config.id,
    //                                 this.env.pos.pos_session.id,
    //                                 order.name
    //                             );                            
    //                         }else{
    //                             await this.showPopup('ErrorPopup', {
    //                                 body: this.env._t('Change QTY transaction failed!'),                    
    //                             });      
    //                         }
    //                     }
    //                 }else{                       
    //                     const { payload: password } = await this.showPopup('PasswordInputPopup', {
    //                         title: this.env._t('Supervisor Pin?'),                    
    //                         isInputSelected: true,                        
    //                     }); 
    
    //                     if ( password ){
    //                         var supervisor = this.env.pos.res_users_supervisor_by_rfid[password];
    //                         if (supervisor) {                                                     
    //                             // if (!this.props.order) return;                    
    //                             var order    = this.env.pos.get_order();
    //                             var line    = order.get_selected_orderline();
    //                             line.set_quantity(reasonPayload);
    //                             this.posActivityLog.saveLogToLocalStorage(
    //                                 'Product Screen',
    //                                 'Change QTY',
    //                                 this.env.pos.user.id,
    //                                 order.cashier.id,
    //                                 this.env.pos.config.id,
    //                                 this.env.pos.pos_session.id,
    //                                 order.name
    //                             );
    //                         }else{
    //                             await this.showPopup('ErrorPopup', {
    //                                 body: this.env._t('Reprint transaction failed!'),                    
    //                             });       
    //                         }
    //                     }                            
    //                 }                    
                    
    //             }
    //         }else{
    //             const {payload: reasonPayload} = await this.showPopup("NumberPopup", {
    //                   title: this.env._t('Change QTY?'),
    //             });
    //             if(reasonPayload){
    //                 const { payload: password } = await this.showPopup('PasswordInputPopup', {
    //                     title: this.env._t('Supervisor Pin?'),                    
    //                     isInputSelected: true,                        
    //                 }); 

    //                 if ( password ){
    //                     var supervisor = this.env.pos.res_users_supervisor_by_rfid[password];
    //                     if (supervisor) {                                                     
    //                         // if (!this.props.order) return;                    
    //                         var order    = this.env.pos.get_order();
    //                         var line    = order.get_selected_orderline();
    //                         line.set_quantity(reasonPayload);
    //                         this.posActivityLog.saveLogToLocalStorage(
    //                             'Product Screen',
    //                             'Changet Qty',
    //                             this.env.pos.user.id,
    //                             order.cashier.id,
    //                             this.env.pos.config.id,
    //                             this.env.pos.pos_session.id,
    //                             order.name
    //                         );
    //                     }else{
    //                         await this.showPopup('ErrorPopup', {
    //                             body: this.env._t('Change QTY transaction failed!'),                    
    //                         });       
    //                     }
    //                 }  
    //             }
    //         }
    //    }
   }

   OrderLineChangeQty.template = 'OrderLineChangeQty';
   ProductScreen.addControlButton({
       component: OrderLineChangeQty,
       condition: function() {
           return this.env.pos;
       },
   });
   Registries.Component.add(OrderLineChangeQty);
   return OrderLineChangeQty;
});