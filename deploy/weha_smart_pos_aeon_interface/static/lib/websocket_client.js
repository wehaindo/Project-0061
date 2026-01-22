class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.websocket = null;
        
        this.onOpen = () => {};
        this.onClose = () => {};
        this.onMessage = () => {};
        this.onError = () => {};
    }
    
    connect() {
        this.websocket = new WebSocket(this.url);
        
        this.websocket.onopen = (event) => {
        this.onOpen(event);
        };
        
        this.websocket.onclose = (event) => {
        this.onClose(event);
        };
        
        this.websocket.onmessage = (event) => {
        this.onMessage(event.data);
        };
        
        this.websocket.onerror = (event) => {
        this.onError(event);
        };
    }
    
    send(message) {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
        this.websocket.send(message);
        } else {
        console.error("WebSocket is not open.");
        }
    }
    
    close() {
        if (this.websocket) {
        this.websocket.close();
        }
    }
}
      
