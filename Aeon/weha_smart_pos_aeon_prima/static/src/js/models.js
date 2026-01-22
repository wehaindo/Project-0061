odoo.define('weha_smart_pos_aeon_prima.models', function (require) {
    var { Order, Orderline, Payment } = require('point_of_sale.models');
    var models = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var PaymentPrima = require('weha_smart_pos_aeon_prima.PaymentPrima');
    
    models.register_payment_method('prima', PaymentPrima);
    

    const PrimaOrder = (Order) => 
    class extends Order{
        add_paymentline(payment_method) {
            var paymentline = super.add_paymentline(payment_method);        
            if (paymentline.payment_method.use_payment_terminal === 'prima'){
                paymentline.set_payment_status('pending');
            }            
            return paymentline;
        }
    }

    Registries.Model.extend(Order, PrimaOrder);

    const PrimaPayment = (Payment) => 
    class extends Payment {
        
        constructor(obj, options) {
            super(...arguments);   
            this.is_prima = this.is_prima || false;                 
            this.partner_reference_no = this.partner_reference_no || '';          
            this.reference_no = this.reference_no || '';
            this.external_id = this.external_id || '';      
            this.transaction_hash = this.transaction_hash || '';
            this.transaction_date = this.transaction_date || ''; 
            this.service_code = this.service_code || '';
            this.invoice_number = this.invoice_number || '';
            this.transaction_id = this.transaction_id || '';
            this.refund_reference_no = this.refund_reference_no || '';
            this.refund_time = this.refund_time || '';
        }

        set_is_prima(is_prima){
            this.is_prima = is_prima;
        }

        get_is_prima(){
            return this.is_prima;
        }
        
        set_partner_reference_no(partner_reference_no){
            this.partner_reference_no = partner_reference_no;

        }

        get_partner_reference_no(){
            return this.partner_reference_no;
        }

        set_reference_no(reference_no){
            this.reference_no = reference_no;

        }

        get_reference_no(){
            return this.reference_no;
        }

        set_external_id(external_id){
            this.external_id = external_id;
        }

        get_external_id(){
            return this.external_id;
        }

        set_transaction_hash(transaction_hash){
            this.transaction_hash = transaction_hash;
        }

        get_transaction_hash(){
            return this.transaction_hash;
        }

        set_transaction_date(transaction_date){
            this.transaction_date = transaction_date;
        }

        get_transaction_date(){
            return this.transaction_date
        }

        set_service_code(service_code){
            this.service_code = service_code;
        }

        get_service_code(){
            return this.service_code;
        }

        set_invoice_number(invoice_number){
            this.invoice_number = invoice_number;
        }

        get_invoice_number(){
            return this.invoice_number;
        }

        set_transaction_id(transaction_id){
            this.transaction_id = transaction_id;
        }

        get_transaction_id(){
            return this.transaction_id;
        }

        set_refund_reference_no(refund_reference_no){
            this.refund_reference_no = refund_reference_no;
        }

        get_refund_reference_no(){
            return this.refund_reference_no;
        }

        set_refund_time(refund_time){
            this.refund_time = refund_time;
        }

        get_refund_time(){
            return this.refund_time;
        }
        
        init_from_JSON(json){
            super.init_from_JSON(...arguments);            
            this.is_prima = json.is_prima;
            this.partner_reference_no = json.partner_reference_no;
            this.reference_no = json.reference_no;
            this.external_id = json.external_id;
            this.transaction_hash = json.transaction_hash;
            this.transaction_date = json.transaction_date;
            this.service_code = json.service_code;
            this.invoice_number = json.invoice_number;
            this.transaction_id = json.transaction_id;        
            this.refund_reference_no = json.refund_reference_no;
            this.refund_time = json.refund_time;    
        }
        
        export_as_JSON(){
            var json = super.export_as_JSON();            
            json.is_prima = this.is_prima;
            json.partner_reference_no = this.partner_reference_no;
            json.reference_no = this.reference_no;
            json.external_id = this.external_id;
            json.transaction_hash = this.transaction_hash;
            json.transaction_date = this.transaction_date;
            json.service_code = this.service_code;
            json.invoice_number = this.invoice_number;
            json.transaction_id = this.transaction_id;
            json.refund_reference_no = this.refund_reference_no;
            json.refund_time = this.refund_time;
            return json;
        }
        
        clone(){
            var payment = super.clone();            
            payment.is_prima = this.is_prima;
            payment.partner_reference_no = this.partner_reference_no;
            payment.reference_no = this.reference_no;
            payment.external_id = this.external_id;
            payment.transaction_hash = this.transaction_hash;
            payment.transaction_date = this.transaction_date;
            payment.service_code = this.service_code;
            payment.invoice_number = this.invoice_number;
            payment.transaction_id = this.transaction_id;
            payment.refund_reference_no = this.refund_reference_no;
            payment.refund_time = this.refund_time;
            return payment;
        }

        export_for_printing(){
            var printing = super.export_for_printing();            
            printing.is_prima = this.is_prima;
            printing.order_name = this.order.name;
            printing.session_name = this.pos.pos_session.name;
            printing.creation_date = this.order.formatted_validation_date;
            printing.user_name = this.pos.user.name;
            printing.pan = this.pan;
            printing.terminal_id = this.terminal_id;
            printing.merchant_id = this.merchant_id;
            printing.reference_no = this.reference_no;
            printing.transaction_date = this.transaction_date;
            printing.service_code = this.service_code;
            printing.transaction_id = this.transaction_id;            
            return printing;
        }
    }

    Registries.Model.extend(Payment, PrimaPayment);
});