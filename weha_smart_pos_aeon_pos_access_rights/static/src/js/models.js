odoo.define('weha_smart_pos_aeon_pos_access_rigths.models', function (require) {
    "use strict";

var { PosGlobalState } = require('point_of_sale.models');
const Registries = require('point_of_sale.Registries');


const PosAccessRightsPosGlobalState = (PosGlobalState) => 
    class extends PosGlobalState {
        async _processData(loadedData) {
            await super._processData(...arguments);
            if (this.config.use_store_access_rights) {
                this.res_users_supervisors = loadedData['res.users.supervisor'];
                this.res_users_supervisor_by_id = loadedData['res.users.supervisor.by.id'];                
                this.res_users_supervisor_by_rfid = loadedData['res.users.supervisor.by.rfid'];                
            }
            if (this.config.module_pos_hr) {                
                this.employee_by_user_id = loadedData['employee_by_user_id'];      
                this.employee_by_id = loadedData['employee_by_id'];          
            }
        }
    }


Registries.Model.extend(PosGlobalState, PosAccessRightsPosGlobalState);

});
