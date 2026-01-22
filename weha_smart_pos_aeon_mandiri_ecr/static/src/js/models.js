odoo.define('weha_smart_pos_aeon_mandiri_ecr.models', function (require) {
    var { Order, Orderline, Payment } = require('point_of_sale.models');
    var models = require('point_of_sale.models');
    var PaymentMandiriEcr = require('weha_smart_pos_aeon_mandiri_ecr.PaymentMandiriEcr');    
    const Registries = require('point_of_sale.Registries');
    
    models.register_payment_method('mandiriecr', PaymentMandiriEcr);
    

    const MandiriEcrOrder = (Order) => 
    class extends Order{
        add_paymentline(payment_method) {
            var paymentline = super.add_paymentline(payment_method);                   
            return paymentline;
        }
    }

    Registries.Model.extend(Order, MandiriEcrOrder);    
});