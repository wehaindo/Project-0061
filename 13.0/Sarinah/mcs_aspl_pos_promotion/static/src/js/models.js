odoo.define('mcs_aspl_pos_promotion.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');

	models.load_fields('product.product',['owner_id']);

    models.load_fields('res.partner',['member_type']);
    });