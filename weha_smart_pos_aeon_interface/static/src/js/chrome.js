odoo.define('weha_smart_pos_aeon_interface', function(require){
    'use strict'

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    // const { WebSocketClient } = require('weha_smart_pos_aeon_interface.WebSocketClient');

    const PosInterfaceChrome = (Chrome) =>
    class extends Chrome {
        /**
         * @override
         */
        setup(){
            super.setup();
            useListener('send-pos-interface', this._sendMessage);
            // this.connectWebsocketServer();
        }

        async start() {
            await super.start();
            await this.connectToInterface();
        }

        async connectWebsocketServer(){
            const client = new WebSocketClient("ws://localhost:1377");
            console.log("Connection to WebsocketServer established!");

            this.client.onOpen = (event) => {
              console.log("WebSocket connection opened.");
              client.send("Hello, server!");
            };
            
            client.onMessage = (message) => {
              console.log("Received message from server:", message);
            };
            
            client.onClose = (event) => {
              console.log("WebSocket connection closed.");
            };
            
            client.onError = (event) => {
              console.error("WebSocket error:", event);
            };            
            client.connect();
        }

        async connectToInterface(){
            console.log("Start Connection to POS Interface");
            this.pos_interface_conn = new WebSocket('ws://localhost:1337');                
            this.pos_interface_conn.onopen = function (e) {
                this.pos_interface_conn_status = true;
                console.log("Connection to pos interface established!");
            };
             // callback messages
            this.pos_interface_conn.onmessage = function (e) {
                // var data = JSON.parse(e.data);
                // console.log(data);
                console.log(e.data);
            };   
        }

        get_pos_interface_conn_status(){
            return this.pos_interface_conn_status;
        }

        _sendMessage(data) {
            console.log("_sendMessage");
            if (this.pos_interface_conn_status === false) return;
            var data = JSON.stringify(data);
            this.pos_interface_conn.send(data);
        }
    }

    Registries.Component.extend(Chrome, PosInterfaceChrome);

    return Chrome;
});