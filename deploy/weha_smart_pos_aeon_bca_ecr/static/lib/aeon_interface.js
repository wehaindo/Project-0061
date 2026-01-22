class WebSocketConnection {
    
    constructor(){
        var status = false;
        this.conn = new WebSocket('ws://localhost:1337');
        this.conn.onopen = function (e) {                
            console.log("Interface Connection have an established!");
            this.status = true;
        };
        // callback messages
        this.conn.onmessage = function (e) {
            var self = this;
            console.log(e.data);               
            this.processMessage(payload);
        };
        // close 
        this.conn.onclose = function (e){
            var self = this;
            console.log("Close Session");
        }   
    }

    waitForOpenSocket(socket) {
        return new Promise((resolve, _reject) => {
          while (socket.readyState !== socket.OPEN) { /* no-op */ }
          console.log('waitForOpenSocket ready')
          return resolve()
        })
    }
      
    async sendMessage(socket, msg) {
        await this.waitForOpenSocket()
        socket.send(msg)
    }

    waitForSocketConnection(socket, callback){
        setTimeout(
            function () {
                var self = this;
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
 
    // sendMessage(socket, data) {
    //     console.log("sendMessage");
    //     // socket.send(data);
    //     this.waitForSocketConnection(socket, function(){
    //         console.log("message sent!!!");
    //         socket.send(data);
    //     });
    // }

    processMessage(payload){
        console.log("Parent class : "  + payload);
    }
    
}