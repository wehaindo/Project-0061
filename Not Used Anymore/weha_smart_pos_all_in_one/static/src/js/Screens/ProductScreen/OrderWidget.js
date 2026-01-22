odoo.define('weha_pos.OrderWidget', function(require){
    'use strict';
    
    const { useState, useRef, onPatched } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const PosComponent = require('point_of_sale.PosComponent');
    const OrderWidget = require('point_of_sale.OrderWidget');
    const Registries = require('point_of_sale.Registries');

    const PosOrderWidget = OrderWidget =>
        class extends OrderWidget {   
            constructor(){
                super(...arguments)
                useListener('delete-button', this.deleteOrderLine);
            }

            async deleteOrderLine(event){
                var self = this;
                const line = this.env.pos.get_order().selected_orderline;
                const { confirmed, payload } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Delete Order Line'),
                    body: this.env._t('Are you sure to delete order line ' + line.full_product_name + ' ?'),
                });
                if (confirmed) {
                    console.log("Delete Order Line : " + line.id); 
                    this.env.pos.get_order().remove_orderline(line);
                }
                  
            }
        };

    Registries.Component.extend(OrderWidget, PosOrderWidget);
    return OrderWidget;

});