odoo.define('weha_smart_pos_aeon_interface.ReceiptScreen', function (require) {
    'use strict';

    const ReceiptScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');        

    const AeonInterfaceReceiptScreen = (ReceiptScreen) => 
        class extends ReceiptScreen {
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
            
            orderDone() {
                super.orderDone();
                var data = {
                    "type": "finish_order",
                    "name": "Finish Order",
                    "value": "0"
                }
                this.sendDataToWebSocket(data);
                console.log("Finish Order");
            }
        }

    Registries.Component.extend(ReceiptScreen, AeonInterfaceReceiptScreen);

    return ReceiptScreen;
});