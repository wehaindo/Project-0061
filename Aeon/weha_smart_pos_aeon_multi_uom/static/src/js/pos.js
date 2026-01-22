odoo.define('weha_smart_pos_aeon_multi_uom', function (require) {
"use strict";
    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const PosDB = require('point_of_sale.DB');
    const { PosGlobalState, Orderline } = require('point_of_sale.models');
    const TicketScreen = require('point_of_sale.TicketScreen');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    const MultiUomPosGlobalState = (PosGlobalState) => class MultiUomPosGlobalState extends PosGlobalState {
        async _processData(loadedData) {
             await super._processData(...arguments);
            if (this.config.allow_multi_uom) {
                this.em_uom_list = loadedData['product.multi.uom'];
            }
        }
    }
    Registries.Model.extend(PosGlobalState, MultiUomPosGlobalState);

    PosDB.include({
        init: function(options){
            var self = this;
            this._super(options);
        },
        add_products: function(products){
            console.log("Multi Uom - add_products 1");
            var self = this;
            this._super(products); 
            for(var i = 0, len = products.length; i < len; i++){
                var product = products[i];
                if(product.has_multi_uom && product.multi_uom_ids){
                    console.log(product);
                    // console.log(product.display_name);
                    console.log("Multi Uom - add_products 2");
                    var barcode_list = $.parseJSON(product.new_barcode);
                    console.log(barcode_list);
                    for(var k=0;k<barcode_list.length;k++){
                        console.log(barcode_list[k]);
                        this.product_by_barcode[barcode_list[k]] = product;
                        console.log(this.product_by_barcode[barcode_list[k]]);
                    }
                }
            }
        },
    });

    const PosResProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _barcodeProductAction(code) {
                console.log("_barcodeProductAction");
                var newBarcode = code.base_code;
                var finalBarcode = newBarcode.padEnd(18,'0');
                code.base_code = finalBarcode;
                console.log("_barcodeProductAction");
                console.log(finalBarcode);
                console.log(code.base_code);
                
                const product = this.env.pos.db.get_product_by_barcode(code.base_code)
                if (!product) {
                    return this._barcodeErrorAction(code);
                }
                const options = await this._getAddProductOptions(product);
                // Do not proceed on adding the product when no options is returned.
                // This is consistent with _clickProduct.
                if (!options) return;

                // update the options depending on the type of the scanned code
                if (code.type === 'price') {
                    Object.assign(options, { price: code.value });
                } else if (code.type === 'weight') {
                    Object.assign(options, {
                        quantity: code.value,
                        merge: false,
                    });
                } else if (code.type === 'discount') {
                    Object.assign(options, {
                        discount: code.value,
                        merge: false,
                    });
                }
                this.currentOrder.add_product(product,  options)
                var line = this.currentOrder.get_last_orderline();
                var pos_multi_op = this.env.pos.em_uom_list;
                for(var i=0;i<pos_multi_op.length;i++){
                    if(pos_multi_op[i].barcode == code.code){
                        line.set_quantity(1);
                        line.set_unit_price(pos_multi_op[i].price);
                        line.set_product_uom(pos_multi_op[i].multi_uom_id[0]);
                        line.price_manually_set = true;
                        line.set_uom_name(pos_multi_op[i].uom_name);
                    }
                }
            }
        };

    Registries.Component.extend(ProductScreen, PosResProductScreen);
    
    class MulitUOMWidget extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            useListener('multi_uom_button', this.multi_uom_button);
        }
        multi_uom_button(res){
            var uom_id = res.detail[0];
            var price = res.detail[1];
            var line = this.env.pos.get_order().get_selected_orderline();
            if(line){
                line.set_unit_price(price);
                line.set_product_uom(uom_id);
                line.price_manually_set = true;
            }
            this.cancel();
        }
    }
    MulitUOMWidget.template = 'MulitUOMWidget';
    MulitUOMWidget.defaultProps = {
        confirmText: 'Ok',
        cancelText: 'Cancel',
        title: '',
        body: '',
    };

    Registries.Component.add(MulitUOMWidget);

    class ChangeUOMButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        get selectedOrderline() {
            return this.env.pos.get_order().get_selected_orderline();
        }
        async onClick() {
            if (!this.selectedOrderline) return;
            var modifiers_list = [];
            var product = this.selectedOrderline.get_product();
            var em_uom_list = this.env.pos.em_uom_list;
            var multi_uom_ids = product.multi_uom_ids;
            for(var i=0;i<em_uom_list.length;i++){
                if(multi_uom_ids.indexOf(em_uom_list[i].id)>=0){
                    modifiers_list.push(em_uom_list[i]);
                }
            }
            await this.showPopup('MulitUOMWidget', {
                title: this.env._t(' POS Multi UOM '),
                modifiers_list:modifiers_list,
            });
        }
    }
    ChangeUOMButton.template = 'ChangeUOMButton';

    ProductScreen.addControlButton({
        component: ChangeUOMButton,
        condition: function() {
            return this.env.pos.config.allow_multi_uom;
        },
    });

    Registries.Component.add(ChangeUOMButton);


const PosMultiUomOrderline = (Orderline) => class PosMultiUomOrderline extends Orderline {
        constructor() {
            super(...arguments);
            this.wvproduct_uom = this.wvproduct_uom || '';
            this.uom_name = '';
        }
        set_uom_name(uom_name){
            this.uom_name = uom_name;
        }
        set_product_uom(uom_id){
            this.wvproduct_uom = this.pos.units_by_id[uom_id];
        }

        get_unit(){
            var unit_id = this.product.uom_id;
            if(!unit_id){
                return undefined;
            }
            unit_id = unit_id[0];
            if(!this.pos){
                return undefined;
            }
            return this.wvproduct_uom == '' ? this.pos.units_by_id[unit_id] : this.wvproduct_uom;
        }

        export_as_JSON(){
            var unit_id = this.product.uom_id;
            var json = super.export_as_JSON(...arguments);
            json.product_uom = this.wvproduct_uom == '' ? unit_id[0] : this.wvproduct_uom.id;
            return json;
        }
        init_from_JSON(json){
            super.init_from_JSON(...arguments);
            this.wvproduct_uom = this.pos.units_by_id[json.product_uom];
        }
    }

    Registries.Model.extend(Orderline, PosMultiUomOrderline);

    const PosResTicketScreen = (TicketScreen) =>
        class extends TicketScreen {
        _getToRefundDetail(orderline) {
            var data = super._getToRefundDetail(orderline);
            if(orderline.wvproduct_uom){
                data['orderline']['wvproduct_uom'] = orderline.wvproduct_uom;

            }
            return data;
        }
        _prepareRefundOrderlineOptions(toRefundDetail) {
            var data = super._prepareRefundOrderlineOptions(toRefundDetail);
            const { qty, orderline } = toRefundDetail;
            if(orderline.wvproduct_uom){
                data["extras"]= {'wvproduct_uom': orderline.wvproduct_uom}

            }
            return data;
        }
    }

    Registries.Component.extend(TicketScreen, PosResTicketScreen);
});

