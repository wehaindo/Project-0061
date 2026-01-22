/** @odoo-module **/

import OrderlineCustomerNoteButton from 'point_of_sale.OrderlineCustomerNoteButton';
import ProductInfoButton from 'point_of_sale.ProductInfoButton';
import InvoiceButton from 'point_of_sale.InvoiceButton';
import ReprintReceiptButton from 'point_of_sale.ReprintReceiptButton';
import Registries from 'point_of_sale.Registries';


export const ShopOnOrderlineCustomerNoteButton = (OrderlineCustomerNoteButton) =>
    class ShopOnOrderlineCustomerNoteButton extends OrderlineCustomerNoteButton {
        async onClick() {
            if(this.env.pos.get_order().orderlines.length){
                super.onClick();
            }
            else{
                 await this.showPopup('ErrorPopup', {
                    title: this.env._t('Warning.'),
                    body: this.env._t('PLeast Select At Least One Product.')
                });
            }
        }
    };

Registries.Component.extend(OrderlineCustomerNoteButton, ShopOnOrderlineCustomerNoteButton);


export const ShopOnProductInfoButton = (ProductInfoButton) =>
    class ShopOnProductInfoButton extends ProductInfoButton {
        async onClick() {
            if(this.env.pos.get_order().orderlines.length){
                super.onClick();
            }
            else{
               await this.showPopup('ErrorPopup', {
                    title: this.env._t('Warning.'),
                    body: this.env._t('PLeast Select At Least One Product.')
                });
            }
        }
    };

Registries.Component.extend(ProductInfoButton, ShopOnProductInfoButton);

export const ShopOnInvoiceButton = (InvoiceButton) =>
    class ShopOnInvoiceButton extends InvoiceButton {
        async _onClick() {
            if(this.props.order){
                super._onClick();
            }
            else{
               await this.showPopup('ErrorPopup', {
                    title: this.env._t('Warning.'),
                    body: this.env._t('PLeast select at least one order.')
                });
            }
        }
    };

Registries.Component.extend(InvoiceButton, ShopOnInvoiceButton);

export const ShopOnReprintReceiptButton = (ReprintReceiptButton) =>
    class ShopOnReprintReceiptButton extends ReprintReceiptButton {
        async _onClick() {
            if(this.props.order){
                super._onClick();
            }
            else{
               await this.showPopup('ErrorPopup', {
                    title: this.env._t('Warning.'),
                    body: this.env._t('PLeast select at least one order.')
                });
            }
        }
    };

Registries.Component.extend(ReprintReceiptButton, ShopOnReprintReceiptButton);
