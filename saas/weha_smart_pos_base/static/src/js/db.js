odoo.define("weha_smart_pos_base.db", function(require) {
    "use strict";

    var DB = require("point_of_sale.DB");
    var { Product } = require('point_of_sale.models');

    var _super_POSDB = DB.prototype;

    var save_prototype = _super_POSDB.save;

    DB.prototype.save = function(store,data){
        console.log("SAVE Prototype");        
        save_prototype.apply(this, arguments);
        if(this.save_order_locally){
            if(store == 'unpaid_orders' || store == 'unpaid_orders_to_remove'){
                return
            }       
            console.log(typeof data);     
            if(data){
                for(let dt of data){
                    var id = dt.id;
                    var order_data = dt.data;         
                    order_data["_id"] = "order_" + dt.id;                                
                    this.save_order_locally_conn.put(order_data);    
                }
            }            
        }
    }

    DB.include({
        
        init: function(options){
            var self = this;
            this._super(options);
        },
                
        set_save_order_locally: function(save_order_locally){
            this.save_order_locally = save_order_locally;
        },

        set_save_order_locally_conn: function(conn){
            this.save_order_locally_conn = conn;
        },
    });

});