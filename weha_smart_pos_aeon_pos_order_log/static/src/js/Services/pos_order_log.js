/** @odoo-module **/

import { registry } from "@web/core/registry";

export const posOrderLogService = {
    dependencies: ["rpc", "pos_notification"],
    start(env, { rpc, pos_notification }) {
        const LOCAL_LOG_KEY = "pos_order_logs";

        function saveLogToLocalStorage(pos_config_id, pos_session_id, pos_reference, pos_order_json) {
            const log = {
                pos_config_id,
                pos_session_id,
                pos_reference,
                pos_order_json,
                date: new Date().toISOString(),
            };
            const logs = JSON.parse(localStorage.getItem(LOCAL_LOG_KEY)) || [];
            logs.push(log);
            localStorage.setItem(LOCAL_LOG_KEY, JSON.stringify(logs));
            console.log("🟡 POS log saved locally:", log);
        }

        async function syncLogsToServer() {
            const orders = JSON.parse(localStorage.getItem(LOCAL_LOG_KEY)) || [];
            if (orders.length === 0) {
                return;
            }

            try {
                const response = await rpc.query({
                    model: "pos.decentralize.order",
                    method: "create_from_ui",
                    args: [orders],
                    silent: true,
                });

                if (response) {
                    localStorage.removeItem(LOCAL_LOG_KEY);
                    console.log("🟢 POS logs synced successfully.");
                }
            } catch (error) {
                console.error("🔴 Failed to sync POS logs:", error);
                // pos_notification.add({
                //     title: "POS Sync Failed",
                //     body: "Unable to sync orders to server. They remain saved locally.",
                //     type: "danger",
                // });
            }
        }

        // Sync every 100 seconds
        setInterval(syncLogsToServer, 100000);

        return {
            saveLogToLocalStorage,
            syncLogsToServer,
        };
    },
};

registry.category("pos_services").add("pos_order_log", posOrderLogService);
