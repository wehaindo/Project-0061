odoo.define('weha_odoo_interface.ReceiptScreen', function(require) {
	'use strict';

	const ReceiptScreen = require('point_of_sale.ReceiptScreen');
	const Registries = require('point_of_sale.Registries');

	const OdooInterfaceReceiptScreen = (ReceiptScreen) => 
		class extends ReceiptScreen {									
			async printReceipt() {
				var self = this;
                if(this.env.pos.config.enable_interface){
                    // Print to Interface
                    console.log("Print To Odoo Interface")
                    console.log(this.currentOrder);
					this.pos_interface_conn = new WebSocket('ws://127.0.0.1:8887');
					this.pos_interface_conn.onopen = function (e) {
						console.log("Connection to pos interface established!");
                        var dataToSend = {
                            type: "print_receipt",
                            data: "[L]\n" +
                                  "[C]" + self.env.pos.config.receipt_header + "\n" +
                                  "[L]\n" +
                                  "[C]" + self.env.pos.config.receipt_footer + "\n" 
                        }
						self._sendMessage(self.pos_interface_conn, JSON.stringify(dataToSend));                               
					};                 
					this.pos_interface_conn.onmessage = function (e) {                    
						console.log(e.data);
						//self.close();
					};
					// close 
					this.pos_interface_conn.onclose = function (e){                
						console.log("Close Session");
					}   

                }else{
                    super.printReceipt();
                }				
			}
			
			waitForSocketConnection(socket, callback){
				var self = this;
                setTimeout(
                    function () {
                        if (socket.readyState === 1) {
                            console.log("Connection is made")
                            if (callback != null){
                                callback();
                            }
                        } else {
                            console.log("wait for connection...")
                            self.waitForSocketConnection(socket, callback);
                        }
            
                    }, 5); // wait 5 milisecond for the connection...
            }
            
            _sendMessage(socket, data) {
                console.log("_sendMessage");
                this.waitForSocketConnection(socket, function(){
					alert("message sent");
                    console.log("message sent!!!");
                    socket.send(data);                    
                });                
            }
			
		}
	
	Registries.Component.extend(ReceiptScreen, OdooInterfaceReceiptScreen);
    return ReceiptScreen;
});