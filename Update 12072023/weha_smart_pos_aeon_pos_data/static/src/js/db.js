odoo.define("weha_smart_pos_aeon_pos_data.db", function(require) {
    "use strict";

    var DB = require("point_of_sale.DB");
    var { Product } = require('point_of_sale.models');

    var _super_POSDB = DB.prototype;

    var save_prototype = DB.prototype.save;

    DB.prototype.save = function(store,data){
        console.log("SAVE Prototype");
        console.log(data);
        save_prototype.apply(this, arguments);
        // Insert Data to CouchDB
        if(this.save_order_locally){
            if(store == 'unpaid_orders' || store == 'unpaid_orders_to_remove'){
                return
            } 
            console.log("Save Order to couchDb");       
            for(let dt of data){
                var id = dt.id;
                var order_data = dt.data;         
                order_data["_id"] = "order_" + dt.id;                                
                this.save_order_locally_conn.put(order_data);    
            }
        }
    }

    DB.include({
        
        init: function(options){
            var self = this;
            this._super(options);
        },
        
        set_is_pouchdb: function(is_pouchdb){
            this.is_pouchdb = is_pouchdb;
        },

        set_pouchdb_conn: function(conn){
            this.pouchdb_conn = conn;
        },


        set_is_product_category_pouchdb: function(is_product_category_pouch_db){
            this.is_product_category_pouch_db = is_product_category_pouch_db;
        },

        set_product_category_pouchdb_conn: function(conn){
            this.product_category_pouch_db_conn = conn;
        },
        
        set_is_product_pricelist_item_pouchdb: function(is_product_pricelist_item_pouch_db){
            this.is_product_pricelist_item_pouch_db = is_product_pricelist_item_pouch_db;
        },

        set_product_pricelist_item_pouchdb_conn: function(conn){
            this.product_pricelist_item_pouch_db_conn = conn;
        },
        set_save_order_locally: function(save_order_locally){
            this.save_order_locally = save_order_locally;
        },

        set_save_order_locally_conn: function(conn){
            this.save_order_locally_conn = conn;
        },

        // save: function(store,data){
        //     console.log("SAVE Prototype");
        //     console.log(data);
        //     var self = this;
        //     this._super(store,data);
        //     if(this.save_order_locally){
        //         if(store == 'unpaid_orders' || store == 'unpaid_orders_to_remove'){
        //             return
        //         } 
        //         console.log("Save Order to couchDb");       
        //         for(let dt of data){
        //             var id = dt.id;
        //             var order_data = dt.data;         
        //             order_data["_id"] = "order_" + dt.id;                                
        //             this.save_order_locally_conn.put(order_data);    
        //         }
        //     }

        // }

        // get_product_by_id: async function(id){
        //     if(this.is_pouchdb){
        //         // console.log('Get Produt By Id from PouchDB');
        //         // var promise = this.pouchdb_conn.find({
        //         //     "selector": {
        //         //        "id": {
        //         //           "$eq": id
        //         //        }
        //         //     }
        //         //  });

        //         // promise.then(
        //         //     function(results){
        //         //         console.log(results);                                                    
        //         //         console.log(results["docs"][0]);
        //         //         return Product.create(results["docs"][0]);
        //         //     }
        //         //  )

        //         // this.pouchdb_conn.query(function (doc, emit) {
        //         //     emit(doc.id);
        //         //   }, {key: id}).then(function (result) {
        //         //     console.log(result);
        //         //   }).catch(function (err) {
        //         //     console.log(err);
        //         //   });
        //         // var product = await this.pouchdb_conn.find({
        //         //     selector: {
        //         //       id: id                      
        //         //     }
        //         // });
        //         // console.log("Create Index by Product ID");
        //         // return this.pouchdb_conn.find({
        //         //             selector: {
        //         //               id: id,                    
        //         //             }                      
        //         //         });
        //         // await this.pouchdb_conn.createIndex({
        //         //     index: {
        //         //       fields: ['id'],
        //         //     }
        //         // }).then(function (){
        //         //     var self = this;
        //         //     return this.pouchdb_conn.find({
        //         //         selector: {
        //         //           id: id,                    
        //         //         }                      
        //         //     });
        //         // });
        //         console.log("Find Product POS Data");
        //         console.log(this.product_by_id);
        //         console.log(this.product_by_id[id]);
        //         return this.product_by_id[id];
        //     }else{
        //         return this.product_by_id[id];
        //     }
        // },

        // get_product_by_barcode: function(barcode){
        //     if(this.is_pouchdb){
        //         console.log('Get Produt By Barcode Is PouchDB');
        //         if(this.product_by_barcode[barcode]){
        //             return this.product_by_barcode[barcode];
        //         } else if (this.product_packaging_by_barcode[barcode]) {
        //             return this.product_by_id[this.product_packaging_by_barcode[barcode].product_id[0]];
        //         }
        //         return undefined;
        //         // var promise = this.pouchdb_conn.find({
        //         //     "selector": {
        //         //        "barcode": {
        //         //           "$eq": barcode
        //         //        }
        //         //     }
        //         //  });

        //         // promise.then(
        //         //     function(results){
        //         //         console.log(results);                            
        //         //     }
        //         // )
        //         // return undefined;
        //     }else{
        //         if(this.product_by_barcode[barcode]){
        //             return this.product_by_barcode[barcode];
        //         } else if (this.product_packaging_by_barcode[barcode]) {
        //             return this.product_by_id[this.product_packaging_by_barcode[barcode].product_id[0]];
        //         }
        //         return undefined;
        //     }
        // },

        // get_product_by_category: function(category_id){
        //     var product_ids  = this.product_by_category_id[category_id];
        //     var list = [];
        //     if (product_ids) {
        //         for (var i = 0, len = Math.min(product_ids.length, this.limit); i < len; i++) {
        //             const product = this.product_by_id[product_ids[i]];
        //             if (!(product.active && product.available_in_pos)) continue;
        //             list.push(product);
        //         }
        //     }
        //     return list;
        // },
    });
});