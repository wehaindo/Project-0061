odoo.define('weha_smart_pos_bca_edc.models', function(require){
    const { register_payment_method, Payment } = require('point_of_sale.models');
    const BcaEdcPayment = require('weha_smart_pos_bca_edc.payment');
    const Registries = require('point_of_sale.Registries');
    register_payment_method('bca_edc', BcaEdcPayment); 
});