
/** @odoo-module */
import { patch } from '@web/core/utils/patch';
import ProductCard from 'point_of_sale.ProductCard';
import Orderline from 'point_of_sale.Orderline';

// Patch product card to show consignment badge
patch(ProductCard.prototype, 'pos_consignment.ProductCard', {
    get badge() {
        try {
            if (this.props.product && this.props.product.is_consignment) {
                return this.env._t('Consignment');
            }
        } catch (e) {}
        return '';
    },
    get badgeClass() {
        return this.props.product && this.props.product.is_consignment ? 'o_pos_consignment_badge' : '';
    }
});

// Extend Orderline model to carry consignment metadata (simplified)
const originalInit = Orderline.prototype.initialize;
Orderline.prototype.initialize = function() {
    originalInit.apply(this, arguments);
    const product = this.get_product && this.get_product();
    this.consignment_contract_id = product && product.consignment_contract_id ? product.consignment_contract_id : null;
    this.consignment_supplier_id = product && product.consignment_supplier_id ? product.consignment_supplier_id : null;
};

const originalExport = Orderline.prototype.export_as_JSON;
Orderline.prototype.export_as_JSON = function() {
    const json = originalExport.apply(this, arguments);
    if (this.consignment_contract_id) {
        json.consignment_contract_id = this.consignment_contract_id;
    }
    if (this.consignment_supplier_id) {
        json.consignment_supplier_id = this.consignment_supplier_id;
    }
    return json;
};
