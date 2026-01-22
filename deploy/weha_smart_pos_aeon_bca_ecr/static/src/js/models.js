odoo.define('weha_smart_pos_aeon_bca_ecr.models', function (require) {
    var { Order, Orderline, Payment } = require('point_of_sale.models');
    var models = require('point_of_sale.models');
    var PaymentBcaEcr = require('weha_smart_pos_aeon_bca_ecr.PaymentBcaEcr');
    const Registries = require('point_of_sale.Registries');
    
    models.register_payment_method('bcaecr', PaymentBcaEcr);

    const BcaEcrPayment = (Payment) => 
    class extends Payment {
        
        constructor(obj, options) {
            super(...arguments);
            this.bca_ecr_data = this.bca_ecr_data || '';
            this.reff_number = this.reff_number || '';
            this.pan = this.pan || '';
            this.approval_code = this.approval_code || '';
            this.merchant_id = this.merchant_id || '';
            this.terminal_id = this.terminal_id || '';
            this.card_holder_name = this.card_holder_name || '';            
        }

        set_bca_ecr_data(bca_ecr_data){
            this.bca_ecr_data = bca_ecr_data;
        }

        set_reff_number(reff_number){
            this.reff_number = reff_number;
        }

        get_reff_number(){
            return this.reff_number;
        }

        set_pan(pan){
            this.pan = pan;
        }

        set_approval_code(approval_code){
            this.approval_code = approval_code;
        }

        set_merchant_id(merchant_id){
            this.merchant_id = merchant_id;
        }

        set_terminal_id(terminal_id){
            this.terminal_id = terminal_id;
        }

        set_card_holder_name(card_holder_name){
            this.card_holder_name = card_holder_name;
        }

        init_from_JSON(json){
            this.bca_ecr_data = json.bca_ecr_data;
            this.reff_number = json.reff_number;
            this.pan = json.pan;
            this.approval_code = json.approval_code;
            this.merchant_id = json.merchant_id;
            this.terminal_id = json.terminal_id;
            this.card_holder_name = json.card_holder_name;            

            super.init_from_JSON(...arguments);
        }
        
        export_as_JSON(){
            var json = super.export_as_JSON();
            json.bca_ecr_data = this.bca_ecr_data;
            json.reff_number = this.reff_number;
            json.pan = this.pan;
            json.approval_code = this.approval_code;
            json.merchant_id = this.merchant_id;
            json.terminal_id = this.terminal_id;
            json.card_holder_name = this.card_holder_name;            

            return json;
        }
        
        clone(){
            var payment = super.clone();
            payment.bca_ecr_data = this.bca_ecr_data;
            payment.reff_number = this.reff_number;
            payment.pan = this.pan;
            payment.approval_code = this.approval_code;
            payment.merchant_id = this.merchant_id;
            payment.terminal_id = this.terminal_id;
            payment.card_holder_name = this.card_holder_name;            
            return payment;
        }
    }

    Registries.Model.extend(Payment, BcaEcrPayment);
});