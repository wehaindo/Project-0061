odoo.define('weha_smart_pos_aeon.interface.PosInterface', function(require){
    'use strict';
    
    var core = require('web.core');

    var PosInterface = core.Class.extend({
        init: function (pos, Product) {
            this.pos = pos;
            this.port = port;
            console.log("Start Connection to POS Interface");       
            this.pos_interface_conn = new WebSocket('ws://localhost:1337');                
            this.pos_interface_conn.onopen = function (e) {
                var self = this;
                console.log("Connection to pos interface established!");
                this.pos_interface_conn_status = true;
                console.log(data);
                console.log(JSON.stringify(data));
                //self.send(JSON.stringify(data));
                console.log("Send Data");
                // this._sendMessage(this.pos_interface_conn, data);                               
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

        },

        send_message: function () {},
        receive_message: function() {},
        close: function () {},
    });
    
    return PosInterface;
});