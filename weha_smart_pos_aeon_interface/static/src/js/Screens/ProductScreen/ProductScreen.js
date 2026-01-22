odoo.define('weha_smart_pos_aeon_interface.ProductScreen', function(require){
    'use strict';

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');

   
    const AeonInterfaceProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            
            async sendDataToWebSocket(data){
                var self = this;
                console.log("Start Connection to POS Interface");       
                this.pos_interface_conn = new WebSocket('ws://localhost:1337');                
                this.pos_interface_conn.onopen = function (e) {
                    console.log("Connection to pos interface established!");
                    this.pos_interface_conn_status = true;
                    self._sendMessage(self.pos_interface_conn, JSON.stringify(data));                               
                };                 
                this.pos_interface_conn.onmessage = function (e) {                    
                    console.log(e.data);
                    //self.close();
                };
                // close 
                this.pos_interface_conn.onclose = function (e){                
                    console.log("Close Session");
                }   
            }
    
            waitForSocketConnection(socket, callback){
                setTimeout(
                    function () {
                        if (socket.readyState === 1) {
                            console.log("Connection is made")
                            if (callback != null){
                                callback();
                            }
                        } else {
                            console.log("wait for connection...")
                            this.waitForSocketConnection(socket, callback);
                        }
            
                    }, 5); // wait 5 milisecond for the connection...
            }
            
            _sendMessage(socket, data) {
                console.log("_sendMessage");
                this.waitForSocketConnection(socket, function(){
                    console.log("message sent!!!");
                    socket.send(data);                    
                });                
            }
            
            async _onClickPay() {
                if (this.env.pos.get_order().orderlines.some(line => line.get_product().tracking !== 'none' && !line.has_valid_product_lot()) && (this.env.pos.picking_type.use_create_lots || this.env.pos.picking_type.use_existing_lots)) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Some Serial/Lot Numbers are missing'),
                        body: this.env._t('You are trying to sell products with serial/lot numbers, but some of them are not set.\nWould you like to proceed anyway?'),
                        confirmText: this.env._t('Yes'),
                        cancelText: this.env._t('No')
                    });
                    if (confirmed) {
                        var order = this.env.pos.get_order();
                        const formattedUnitPrice = this.env.pos.format_currency( order.get_total_with_tax(),'Product Price');
                        var data = {
                            "type": "add_product",
                            "name": "Total Belanja",
                            "value": formattedUnitPrice
                        }
                        this.sendDataToWebSocket(data);
                        this.showScreen('PaymentScreen');
                    }
                } else {
                    var order = this.env.pos.get_order();
                    const formattedUnitPrice = this.env.pos.format_currency( order.get_total_with_tax(),'Product Price');
                    var data = {
                        "type": "add_product",
                        "name": "Total Belanja",
                        "value": formattedUnitPrice
                    }
                    this.sendDataToWebSocket(data);
                    this.showScreen('PaymentScreen');
                }
            }
        }
    
    Registries.Component.extend(ProductScreen, AeonInterfaceProductScreen);

    return ProductScreen;
});