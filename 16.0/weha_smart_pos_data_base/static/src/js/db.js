odoo.define("weha_smart_pos_data_base.db", function(require) {
    "use strict";

    var DB = require("point_of_sale.DB");
    var { Product } = require('point_of_sale.models');

    var _super_POSDB = DB.prototype;

    var save_prototype = DB.prototype.save;
    var get_product_by_id_prototype = DB.prototype.get_product_by_id;
    var get_product_by_barcode_prototype = DB.prototype.get_product_by_barcode;

    DB.prototype.save = function(store,data){
        console.log("SAVE Prototype");
        var self = this;        
        save_prototype.apply(this, arguments);
        // Insert Data to CouchDB
        if(this.save_order_locally){
            if(store == 'unpaid_orders' || store == 'unpaid_orders_to_remove'){
                return
            } 
            console.log("Save Order to couchDb");      
            if(data.length > 0){
                for(let dt of data){
                    var id = dt.id;
                    var order_data = dt.data;         
                    order_data["_id"] = order_data['access_token'];                                
                    this.save_order_locally_conn.put(order_data).then(function (response) {
                        // handle response                        
                        console.log(response);                                                
                        self.save_order_locally_conn.replicate.to(self.pos_orders_pouch_db_conn);
                    }).catch(function (err) {
                        console.error(err);    
                        self.save_order_locally_conn.replicate.to(self.pos_orders_pouch_db_conn);                    
                    });                    
                }
            }            
        }
        
    }

    DB.include({
        
        init: function(options){
            var self = this;
            this._super(options);
        },

        set_pos_global_state: function(pos_global_state){
            this.pos_global_state = pos_global_state;
        },
        
        set_pos: function(pos){
            this.pos = pos;
        },

        set_is_pouchdb: function(is_pouchdb){
            this.is_pouchdb = is_pouchdb;
        },

        set_pouchdb_conn: function(conn){
            this.pouchdb_conn = conn;
        },
        
        set_save_order_locally: function(save_order_locally){
            this.save_order_locally = save_order_locally;
        },

        set_save_order_locally_conn: function(conn){
            this.save_order_locally_conn = conn;
        },

        set_is_pos_orders_pouchdb_conn: function(conn){
            this.pos_orders_pouch_db_conn = conn;
        },

        sync_pos_orders(){
            this.order();
        },   
    });
});