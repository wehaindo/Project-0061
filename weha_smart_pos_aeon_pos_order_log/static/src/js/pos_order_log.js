odoo.define('weha_smart_pos_aeon_pos_order_log.PosOrderLog', function(require) {
    "use strict";

    const PosModel = require('point_of_sale.models');
    const rpc = require('web.rpc');
    const LOCAL_LOG_KEY = 'pos_order_logs';

    class PosOrderLog {
        constructor() {

        }

        // Utility function to save logs in local storage
        saveLogToLocalStorage(pos_config_id, pos_session_id, pos_reference, pos_order_json) {
            console.log("Saving pos order log to local storage");
            var log = {
                pos_config_id: pos_config_id,
                pos_session_id: pos_session_id,
                pos_reference: pos_reference,
                pos_order_json: pos_order_json            
            }
            const logs = JSON.parse(localStorage.getItem(LOCAL_LOG_KEY)) || [];
            logs.push(log);
            console.log(logs);
            localStorage.setItem(LOCAL_LOG_KEY, JSON.stringify(logs));
        }   

        // Function to sync logs to the server
        syncLogsToServer() {

            if (!navigator.onLine) {
                console.log("⛔ Offline: skipping POS log sync.");
                return;
            }

            const orders = JSON.parse(localStorage.getItem(LOCAL_LOG_KEY)) || [];
            if (orders.length === 0) {
                console.log("There are no order logs to sync")
                return;
            } // No logs to sync
            
           
            // Send logs to the server
            // try{
            //     rpc.query({
            //         model: 'pos.decentralize.order',
            //         method: 'create_from_ui',  // Custom server method for batch log creation
            //         args: [orders],
            //     }).then(function(response) {
            //         console.log("Sync Successfully")
            //         if (response) {
            //             // Clear logs from local storage after successful sync
            //             localStorage.removeItem(LOCAL_LOG_KEY);
            //             console.log('Orders successfully synced and cleared from local storage.');
            //         }
            //     });
            // } catch (error) {
            //     console.error('Error while preparing orders for sync:', error);                
            // }

            rpc.query({
                model: 'pos.decentralize.order',
                method: 'create_from_ui',  // Custom server method for batch log creation
                args: [orders],
                silent: true,
            }).then(function(response) {
                console.log("Sync Successfully")
                if (response) {
                    // Clear logs from local storage after successful sync
                    localStorage.removeItem(LOCAL_LOG_KEY);
                    console.log('Orders successfully synced and cleared from local storage.');
                }
            // });            
            }).catch(function(error) {
                console.error('Error syncing logs:', error);
            });
        }

        // Sync logs every 5 minutes (300,000 ms)
       
    }

    var posOrderLog = new PosOrderLog(); 
    setInterval(posOrderLog.syncLogsToServer, 100000);
    return PosOrderLog
});
