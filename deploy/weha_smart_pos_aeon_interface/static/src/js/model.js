odoo.define('weha_smart_pos_aeon_interface.models', function(require){

    var { Order, Orderline, Payment } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var models = require('point_of_sale.models');
        
    const PosInterfaceOrder = (Order) => 
    class extends Order {	
        constructor(obj, options) {
            super(...arguments);
            // WebSocketConnection.prototype.processMessage = this.processMessage;
        }

		add_product(product, options){
            super.add_product(...arguments);            
            var line = this.get_selected_orderline();
            const formattedUnitPrice = this.pos.format_currency(line.get_price_with_tax(),'Product Price');
            var data = {
                type: "add_product",
                name: line.product.display_name,
                value: formattedUnitPrice,
            }
            //Send Data to Pool Display
            this.sendDataToWebSocket(data);
        }

        async sendDataToWebSocket(data){
            console.log("Start Connection to POS Interface");       
            var self = this;
            this.pos_interface_conn = new WebSocket('ws://localhost:1337');                
            this.pos_interface_conn.onopen = function (e) {
                console.log("Connection to pos interface established!");
                self.pos_interface_conn_status = true;
                console.log(data);
                console.log(JSON.stringify(data));
                //self.send(JSON.stringify(data));
                console.log("Send Data");
                self._sendMessage(self.pos_interface_conn, JSON.stringify(data));                               
                // console.log("Close Session");
            };
             // callback messages
            this.pos_interface_conn.onmessage = function (e) {
                // var data = JSON.parse(e.data);
                // console.log(data);
                var self = this;
                console.log(e.data);
                // self.close();
            };
            // close 
            this.pos_interface_conn.onclose = function (e){
                var self = this;
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
    }

    Registries.Model.extend(Order, PosInterfaceOrder);

});