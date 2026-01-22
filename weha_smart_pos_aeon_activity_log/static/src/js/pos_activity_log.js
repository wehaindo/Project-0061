odoo.define('weha_smart_pos_aeon_activity_log.PosActivityLog', function(require) {
    "use strict";

    const PosModel = require('point_of_sale.models');
    const rpc = require('web.rpc');
    const LOCAL_LOG_KEY = 'pos_activity_logs';

    class PosActivityLog {
        constructor() {
        }
        // Utility function to save logs in local storage
        saveLogToLocalStorage(name, details, res_users_id, hr_employee_id, pos_config_id, pos_session_id, pos_order_reference) {
            var log = {
                name: name,
                details: details,
                user_id: res_users_id,
                hr_employee_id: hr_employee_id,
                pos_config_id: pos_config_id,
                pos_session_id: pos_session_id,
                pos_order_reference : pos_order_reference
            }
            const logs = JSON.parse(localStorage.getItem(LOCAL_LOG_KEY)) || [];
            logs.push(log);
            console.log(logs);
            localStorage.setItem(LOCAL_LOG_KEY, JSON.stringify(logs));
        }   

        // Function to sync logs to the server
        syncLogsToServer() {
            const logs = JSON.parse(localStorage.getItem(LOCAL_LOG_KEY)) || [];
            if (logs.length === 0) {
                console.log("There are no logs to sync")
                return;
            } // No logs to sync

            // Send logs to the server
            // try{
            //     rpc.query({
            //         model: 'pos.activity.log',
            //         method: 'create_from_ui',  // Custom server method for batch log creation
            //         args: [logs],
            //     }).then(function(response) {
            //         console.log("Sync Successfully")
            //         if (response) {
            //             // Clear logs from local storage after successful sync
            //             localStorage.removeItem(LOCAL_LOG_KEY);
            //             console.log('Logs successfully synced and cleared from local storage.');
            //         }
            //     });
            // }catch (error) {
            //     console.error('Error while preparing logs for sync:', error);                
            // }
            
            rpc.query({
                model: 'pos.activity.log',
                method: 'create_from_ui',  // Custom server method for batch log creation
                args: [logs],
            }).then(function(response) {
                console.log("Sync Successfully")
                if (response) {
                    // Clear logs from local storage after successful sync
                    localStorage.removeItem(LOCAL_LOG_KEY);
                    console.log('Logs successfully synced and cleared from local storage.');
                }
            // });
            }).catch(function(error) {
                console.error('Error syncing logs:', error);
            });
        }
        // Sync logs every 5 minutes (300,000 ms)
       
    }

    var posActivityLog = new PosActivityLog(); 
    setInterval(posActivityLog.syncLogsToServer, 100000);
    return PosActivityLog
});
