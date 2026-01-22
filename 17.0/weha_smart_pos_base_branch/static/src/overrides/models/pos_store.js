/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";


patch(PosStore.prototype, {

    async logoutPos() {
        window.location = '/pos/login/' + this.config.pos_config_code;
    },

    // Multiple barcode
    async _loadProductBarcode(loadedData){
        var self = this;
        console.log('loadProductBarcode');
        var product_template_barcodes = loadedData['product.template.barcode'];                          
        product_template_barcodes.forEach(function(product_barcode){
            var product = self.db.product_by_id[product_barcode['product_product_id']]
            if(product){
                self.db.product_by_barcode[product_barcode['barcode']] = product;                
            }
        })
        console.log(this.db.product_by_barcode);
    },

    //Support Channel
    async _loadDiscussChannel(loadedData){
        this.discuss_channels = loadedData['discuss.channel'];
    },


    //@override
    async _processData(loadedData) {
        await super._processData(...arguments);
        if (this.config.use_store_access_rights) {
            this.hr_employee_supervisors = loadedData['hr.employee.supervisor'];
            this.hr_employee_supervisor_by_id = loadedData['hr.employee.supervisor.by.id'];                
            this.hr_employee_supervisor_by_rfid = loadedData['hr.employee.supervisor.by.rfid'];                
        }
        await this._loadProductBarcode(loadedData);
        await this._loadDiscussChannel(loadedData);
    },
});