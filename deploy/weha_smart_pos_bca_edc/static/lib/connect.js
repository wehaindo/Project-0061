/**
 * Connection / Communications with server
 */
var ConnectWS = {
    connection: null,
    connection_status: false,
    ip_address: 'localhost', // edit by yours
    port: '1337', // port

    start: function () {
        console.log("Start Connection to localhost websocket");
        this.connection = new WebSocket('ws://' + this.ip_address + ':' + this.port);

        this.connection.onopen = function (e) {
            Connect.connection_status = true;
            console.log("Connection established!");

            $('.window .title').html('Connected.');
        };

        // callback messages
        this.connection.onmessage = function (e) {
            // var data = JSON.parse(e.data);
            // console.log(data);
            console.log(e);
        };

        // Closed window
        this.connection.onclose = function (e) {
            console.log("Connection closed!");
            this.connection_status = false;
        };

        // Error window
        this.connection.onerror = function (e) {
            console.log("Connection error!");
            this.connection_status = false;
        };

    },

    sendMessage: function (data) {
        if (this.connection_status === false) return;

        var data = JSON.stringify(data);
        this.connection.send(data);
    },

};
