odoo.define("weha_smart_pos_aeon_pos_data.db", function(require) {
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
        // console.log(data);       
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

    DB.prototype.add_product_categories = function(product_categories){
        console.log("Add Product Categories");
        this.product_category_by_id = {}
        for(var i = 0, len = product_categories.length; i < len; i++){
            var product_category = product_categories[i];
            this.product_category_by_id[product_category.id] = product_category;
        }        
    }

    DB.prototype.get_product_category_by_id = function(id){
        return this.product_category_by_id[id];
    }

    DB.prototype.add_product_subcategories = function(product_subcategories){
        console.log("Add Produc Sub Categories");
        this.product_subcategory_by_id = {}
        for(var i = 0, len = product_subcategories.length; i < len; i++){
            var product_subcategory = product_subcategories[i];
            this.product_subcategory_by_id[product_subcategory.id] = product_subcategory;
        }        
    }

    DB.prototype.get_product_sub_category_by_id = function(id){
        return this.product_subcategory_by_id[id];
    }


    // DB.prototype.get_product_by_id = function(id){
    //     console.log("get_product_by_id");
    //     console.log(id)
    //     if(this.is_pouchdb){
    //         console.log('Get Produt By Id from PouchDB');            
    //         return this.get_local_product_by_id(id);
    //     }else{            
    //         return get_product_by_id_prototype.apply(this, arguments);
    //     }
    // }

    // DB.prototype.get_product_by_barcode = async function(barcode){        
    //     console.log('get_product_by_barcode');
    //     var self = this;
    //     var product = this.product_by_barcode[barcode];
    //     console.log(product);
    //     if(product){
    //         console.log('Product Found');
    //         return product;
    //     }else{
    //         console.log('Product not Found');
    //         console.log('find_local_product_by_barcode');
    //         await this.pos_global_state._get_local_product_by_barcode(barcode).then(function(products){
    //             console.log('_loadProductProduct');
    //             self.pos_global_state._loadProductProduct(products)
    //             return self.product_by_barcode[barcode];
    //         });
    //         console.log('finish_find_local_product_by_barcode')
    //     }       
    //     console.log('end_get_product_by_barcode'); 
    // }

    // DB.prototype.get_product_by_barcode = async function(barcode){
    //     console.log('get_product_by_barcode inherit')
    //     var self = this;
    //     // if(self.is_pouchdb){
    //     self.pouchdb_conn.createIndex({
    //         index: {fields:['barcode']}                    
    //     }).then(function() {
    //         self.pouchdb_conn.find({
    //             selector: {
    //                 'barcode': barcode
    //             }
    //     }).then((products) => {
    //         console.log('products');
    //         console.log(products)
    //         console.log(products['docs'][0]);
    //         var product = products['docs'][0];                                
    //         product.pos = self.pos;
    //         product.applicablePricelistItems = {};
    //         var product_obj = Product.create(product)
    //         console.log('product_obj');
    //         console.log(product_obj);
    //         return Product.create(product_obj);
    //     }).catch((err) => {
    //         return undefined;
    //     });


                // var result  =  await self.pouchdb_conn.find({
                //     selector: {
                //         'barcode': barcode
                //     }
                // })
                // console.log('result');
                // console.log(result)
                // console.log(result['docs'][0]);
                // var product = result['docs'][0];                                
                // product.pos = self.pos;
                // product.applicablePricelistItems = {};
                // // productMap[product.id] = product;
                // // productTemplateMap[product.product_tmpl_id[0]] = (productTemplateMap[product.product_tmpl_id[0]] || []).concat(product);
                // var product_obj = Product.create(product)
                // console.log('product_obj');
                // console.log(product_obj);
                // return Product.create(product_obj);
                // var product_obj = Product.create(product)
                // console.log(product_obj);
                // return product_obj;
    //         })
    //     // }
    // }

    // DB.prototype.get_product_by_barcode = async function(barcode){
    //     console.log("get_product_by_barcode");
    //     console.log(barcode);
    //     if(this.is_pouchdb){
    //         console.log('Get Produt By Barcode Is PouchDB');
    //         await this.pouchdb_conn.find({
    //             "selector": {
    //                 "barcode": {
    //                     "$eq": barcode
    //                 }
    //             }
    //         }).then(function(result){
    //             console.log(result); 
    //             return result.docs[0];
    //         }).catch(function(err){
    //             console.log("err");
    //             console.log(err);
    //             return undefined;
    //         })            
    //     }else{
    //         if(this.product_by_barcode[barcode]){
    //             return this.product_by_barcode[barcode];
    //         } else if (this.product_packaging_by_barcode[barcode]) {
    //             return this.product_by_id[this.product_packaging_by_barcode[barcode].product_id[0]];
    //         }
    //         return undefined;
    //     }
    // }

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

        set_is_product_barcode_pouchdb: function(is_product_barcode_pouch_db){
            this.is_product_barcode_pouch_db = is_product_barcode_pouch_db;
        },

        set_product_barcode_pouchdb_conn: function(conn){
            this.product_barcode_pouch_db_conn = conn;
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

        set_is_pos_orders_pouchdb_conn: function(conn){
            this.pos_orders_pouch_db_conn = conn;
        },

        sync_pos_orders(){
            this.order();
        },

        get_local_product_by_id: function(models, product_id){

        },

        find_local_product_by_barcode: async function(code){
            var self = this;
            let promise = new Promise((resolve, reject) => {
                self.pos_global_state.get_local_product_by_barcode(code)
                resolve();
            });
            let result = await promise;
            return result;
        },
        //     console.log('get_product_by_barcode inherit')
        //     var self = this;            
        //     self.pouchdb_conn.createIndex({
        //         index: {fields:['barcode']}                    
        //     }).then(function() {
        //         self.pouchdb_conn.find({
        //             selector: {
        //                 'barcode': barcode
        //             }
        //     }).then((products) => {
        //         console.log('products');
        //         console.log(products)
        //         console.log(products['docs'][0]);
        //         var product = products['docs'][0];                                
        //         models.loadProductProduct(products);
        //     }).catch((err) => {
        //         return undefined;
        //     });            
        // }

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
        //         console.log('Get Produt By Id from PouchDB');
        //         var promise = this.pouchdb_conn.find({
        //             "selector": {
        //                "id": {
        //                   "$eq": id
        //                }
        //             }
        //          });

        //         promise.then(
        //             function(results){
        //                 console.log("get_product_by_id");
        //                 console.log(results);                                                    
        //                 console.log(results["docs"][0]);
        //                 return Product.create(results["docs"][0]);
        //             }
        //          )
        //         } else {
        //             return super.get_product_by_id(id);
        //         }


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