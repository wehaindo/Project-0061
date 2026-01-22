odoo.define('weha_smart_posa_base.models', function(require){
    "use strict";

    var models = require('point_of_sale.models');
    var { PosCollection, PosModel, PosGlobalState, Order, Orderline, Product } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const BaseGlobalState = (PosGlobalState) => 
    class  extends PosGlobalState {
        constructor(obj) {
            super(obj);            
        } 
                
        async _processData(loadedData) {
            await super._processData(...arguments);
            if (this.config.use_store_access_rights) {
                this.res_users_supervisors = loadedData['res.users.supervisor'];
                this.res_users_supervisor_by_id = loadedData['res.users.supervisor.by.id'];                
                this.res_users_supervisor_by_rfid = loadedData['res.users.supervisor.by.rfid'];                
            }
        }        
        async after_load_server_data(){           
            await this.connectOrdersDB();                                        
            await super.after_load_server_data();
        }

        async connectOrdersDB(){
            console.log(this.config);      
            if(this.config.is_backup_order_to_localstorage){
                this.ordersPouchDB = await new PouchDB('Orders');
                this.db.set_save_order_locally(true);
                this.db.set_save_order_locally_conn(this.ordersPouchDB);
            }
        }
    }

    Registries.Model.extend(PosGlobalState, BaseGlobalState);

    const BaseOrder = (Order) => 
    class extends Order {    
        constructor(obj, options){
            super(...arguments);               
            this.is_refund = this.is_refund || false;           
            this.refund_parent_pos_reference = this.refund_parent_pos_reference || '';
        }

        get_is_refund(){
            return this.is_refund;
        }

        set_is_refund(is_refund){
            this.is_refund = is_refund;
        }

        get_refund_parent_pos_reference(){
            return this.refund_parent_pos_reference;
        }

        set_refund_parent_pos_reference(refund_parent_pos_reference){
            this.refund_parent_pos_reference = refund_parent_pos_reference;
        }

        add_paymentline(payment_method) {
            if (this.pos.config.is_only_one_payment_line){
                var paylmentline_count = this.get_paymentlines().length;
                if (paylmentline_count == 0 ){
                    var paymentline = super.add_paymentline(payment_method);            
                    return paymentline;    
                }else{
                    return false;
                }
            }else{
                return super.add_paymentline(payment_method);
            }            
        }

        get_receipt_logo_url(){
            return window.location.origin + "/web/image?model=pos.config&field=pos_receipt_logo_img&id=" + this.pos.config.id;
        }
    
        get_receipt_global_logo_url(){
            return window.location.origin + "/web/image?model=res.company&field=pos_global_receipt_logo_img&id=" + this.pos.company.id;
        }
    
        
        clone(){
            const order = super.clone(...arguments);
            order.is_refund = this.is_refund;
            order.refund_parent_pos_reference = this.refund_parent_pos_reference;
            return order;
        }

        init_from_JSON(json){
            super.init_from_JSON(...arguments);            
            this.is_refund = json.is_refund;
            this.refund_parent_pos_reference = json.refund_parent_pos_reference;            
        }

        export_as_JSON(){
            const json = super.export_as_JSON(...arguments);            
            json.is_refund=this.is_refund;
            json.refund_parent_pos_reference = this.refund_parent_pos_reference;
            return json;
        }

        export_for_printing() {
            const result = super.export_for_printing(...arguments);
            result.is_show_receipt_logo = this.pos.config.is_show_receipt_logo;
            result.receipt_logo_url = this.get_receipt_logo_url();
            result.receipt_global_logo_url = this.get_receipt_global_logo_url();        
            return result;
        }
    }

    Registries.Model.extend(Order, BaseOrder);
});