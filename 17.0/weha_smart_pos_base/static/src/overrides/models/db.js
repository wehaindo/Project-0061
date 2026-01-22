/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosDB } from "@point_of_sale/app/store/db";



patch(PosDB.prototype, {
    set_pos_orders_pouchdb_conn(conn){
        this.pos_orders_pouch_db_conn = conn;
    },
    set_is_save_order_to_local_db(value){
        this.is_save_order_to_local_db = value;
    },
    add_products(products){        
        super.add_products(products); 
        // POS Multi UOM
        for(var i = 0, len = products.length; i < len; i++){
            var product = products[i];
            if(product.has_multi_uom && product.multi_uom_ids){                                                
                var barcode_list = JSON.parse(product.new_barcode);
                console.log(barcode_list);
                for(var k=0;k<barcode_list.length;k++){                    
                    this.product_by_barcode[barcode_list[k]] = product;
                    console.log(this.product_by_barcode[barcode_list[k]]);
                }
            }
        }

    },
    save(store, data) {
        super.save(...arguments);        
        //Sync Order Locally     
        if(this.is_save_order_to_local_db){                          
            if(store == 'unpaid_orders' || store == 'unpaid_orders_to_remove'){
                return
            }
            if(data.length > 0){
                for(let dt of data){
                    var id = dt.id;
                    var order_data = dt.data;         
                    order_data["_id"] = order_data['access_token'];                                
                    this.pos_orders_pouch_db_conn.put(order_data).then(function (response) {
                        console.log("Success Save to Local DB");                                                
                    }).catch(function (err) {
                        console.error(err);    
                    });                    
                }
            }
        }        
    }
})