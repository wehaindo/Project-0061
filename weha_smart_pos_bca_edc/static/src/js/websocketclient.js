odoo.define('weha_smart_pos_bca_edc.WebSocketClient', function(require) {
    "use strict";
    // var connection = null;
    // var connection_status = false;
    // var ip_address = 'localhost';
    // var port = '1337';

    // const waitForOpenConnection = (socket) => {
    //     return new Promise((resolve, reject) => {
    //         const maxNumberOfAttempts = 10
    //         const intervalTime = 200 //ms
    
    //         let currentAttempt = 0
    //         const interval = setInterval(() => {
    //             if (currentAttempt > maxNumberOfAttempts - 1) {
    //                 clearInterval(interval)
    //                 reject(new Error('Maximum number of attempts exceeded'))
    //             } else if (socket.readyState === socket.OPEN) {
    //                 clearInterval(interval)
    //                 resolve()
    //             }
    //             currentAttempt++
    //         }, intervalTime)
    //     })
    // }

    class ConnectWS {
        connection = null;
        connection_status = false;
        ip_address = 'localhost';
        port = '1337';


        start() {
            console.log("Start Connection to BCA EDC");
            this.connection = new WebSocket('ws://' + this.ip_address + ':' + this.port);    
            this.connection.onopen = function (e) {
                this.connection_status = true;
                console.log("Connection established!");
            };
             // callback messages
            this.connection.onmessage = function (e) {
                // var data = JSON.parse(e.data);
                // console.log(data);
                console.log(e.data);
            };
        }
        
        waitForOpenConnection() {
            console.log("waitForOpenConnection");
            return new Promise((resolve, reject) => {
                const maxNumberOfAttempts = 10
                const intervalTime = 200 //ms
        
                let currentAttempt = 0
                const interval = setInterval(() => {
                    if (currentAttempt > maxNumberOfAttempts - 1) {
                        clearInterval(interval)
                        reject(new Error('Maximum number of attempts exceeded'))
                    } else if (this.connection.readyState === this.connection.OPEN) {
                        clearInterval(interval)
                        resolve()
                    }
                    currentAttempt++
                }, intervalTime)
            })
        }

        async sendMessage(msg){
            if (this.connection.readyState !== this.connection.OPEN) {
                try {
                    await this.waitForOpenConnection()
                    this.connection.send(msg)                    
                } catch (err) { console.error(err) }
            } else {
                this.connection.send(msg)                
            }            
        }
    }

    // var ConnectWS = {
    //     connection: null,
    //     connection_status: false,
    //     ip_address: 'localhost', // edit by yours
    //     port: '1337', // port
    
    //     start: function () {
    //         console.log("Start Connection to BCA EDC");
    //         this.connection = new WebSocket('ws://' + this.ip_address + ':' + this.port);
    
    //         this.connection.onopen = function (e) {
    //             ConnectWS.connection_status = true;
    //             console.log("Connection established!");
    //             ConnectWS.connection.send("Connection Established");
    //             // $('.window .title').html('Connected.');
    //             ConnectWS.connection.close();
    //         };
    
    //         // callback messages
    //         this.connection.onmessage = function (e) {
    //             // var data = JSON.parse(e.data);
    //             // console.log(data);
    //             console.log(e);
    //         };
    
    //         // Closed window
    //         this.connection.onclose = function (e) {
    //             console.log("Connection closed!");
    //             this.connection_status = false;
    //         };
    
    //         // Error window
    //         this.connection.onerror = function (e) {
    //             console.log("Connection error!");
    //             this.connection_status = false;
    //         };
    
    //     },
    
    //     sendMessage: function (data) {
    //         if (this.connection_status === false) return;
    //         var data = JSON.stringify(data);
    //         this.connection.send(data);
    //     },
    
    // };
    
    return { ConnectWS };
});