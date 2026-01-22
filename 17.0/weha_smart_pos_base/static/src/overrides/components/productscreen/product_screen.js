/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { CashierName } from "@point_of_sale/app/navbar/cashier_name/cashier_name";
import { ErrorBarcodePopup } from "@point_of_sale/app/barcode/error_popup/barcode_error_popup";

patch(ProductScreen.prototype, {    
    components: { ...ProductScreen.components, CashierName },
})

patch(ProductScreen.prototype, {
    setup() {
        super.setup();
        this.posbus = useService('pos_bus');    
        var order = this.pos.get_order();
        // Default Customer
        if (!order.get_partner()) {
            if (this.pos.config.is_set_default_customer && this.pos.config.customer_id) {
                var customer_id = this.pos.db.get_partner_by_id(this.pos.config.customer_id[0]);
                if (customer_id) {
                    order.set_partner(customer_id);
                }
            } else if (this.pos && this.pos.get_order()) {
                this.pos.get_order().set_partner(null);
            }
        }        
    },
    NumpadVisibility() {
        $('.numpad').slideToggle('slow', function() {

            if($('.NumpadVisibility').find('span').hasClass('hd_numpad'))
            {
                $('.NumpadVisibility').find('span').text("Hide Numpad")
                $('.NumpadVisibility').find('span').removeClass('hd_numpad').addClass('dh_numpad');
            }
            else{
                $('.NumpadVisibility').find('span').text("Show Numpad")
                $('.NumpadVisibility').find('span').removeClass('dh_numpad').addClass('hd_numpad');
            }
        });
    },
    _openSideBar(){
        $('.dn_sidebar').show(100)
        $('.open_side_bar_menu').addClass('toggleSidebarMenu')
        if(this.env.isMobile){
            $('.rightpane').addClass('d-none')
            $('.leftpane').addClass('d-none')
            $('.dn_sidebar').addClass('full_dn_sidebar')
        }
    },
    _closeSideBar(){
        $('.dn_sidebar').hide(100)
        $('.open_side_bar_menu').removeClass('toggleSidebarMenu')
        if(this.env.isMobile){
            $('.rightpane').removeClass('d-none')
            $('.leftpane').removeClass('d-none')
            $('.dn_sidebar').removeClass('full_dn_sidebar')
        }
    },
    get totalItems() {
        var order = this.pos.get_order();
        var orderlines = order.orderlines;
        return orderlines.length;
    },
    get totalQuantity(){        
        var order = this.pos.get_order();
        var orderlines = order.orderlines;
        var quantity = 0;
        orderlines.forEach(orderline => {
            quantity = quantity + orderline.get_quantity();
        });
        return quantity;        
        
    },
    async _barcodeProductAction(code) {
        const product = await this._getProductByBarcode(code);
        if (!product) {
            return this.popup.add(ErrorBarcodePopup, { code: code.base_code });
        }
        const options = await product.getAddProductOptions(code);
        // Do not proceed on adding the product when no options is returned.
        // This is consistent with clickProduct.
        if (!options) {
            return;
        }

        // update the options depending on the type of the scanned code
        if (code.type === "price") {
            Object.assign(options, {
                price: code.value,
                extras: {
                    price_type: "manual",
                },
            });
        } else if (code.type === "weight" || code.type === "quantity") {
            Object.assign(options, {
                quantity: code.value,
                merge: false,
            });
        } else if (code.type === "discount") {
            Object.assign(options, {
                discount: code.value,
                merge: false,
            });
        }
        this.currentOrder.add_product(product, options);
        var line = this.currentOrder.get_last_orderline();
        var pos_multi_op = this.pos.em_uom_list;
        for(var i=0;i<pos_multi_op.length;i++){
            if(pos_multi_op[i].barcode == code.code){
                line.set_quantity(1);
                line.set_unit_price(pos_multi_op[i].price);
                line.set_product_uom(pos_multi_op[i].multi_uom_id[0]);
                line.price_manually_set = true;
                line.set_uom_name(pos_multi_op[i].uom_name);
            }
        }      
        this.numberBuffer.reset();       
    },
});


