odoo.define('weha_smart_pos_data_base.models', function(require){
    "use strict";
    
    var { PosGlobalState, Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosDataBasePosGlobalState = (PosGlobalState) => 
    class  extends PosGlobalState {
        constructor(obj) {
            super(obj);
        }

        async after_load_server_data(){
            var self = this;
            if(this.config.use_pos_data_speed_up){
                this.db.set_pos(this.pos);
                await this.db.set_pos_global_state(this);
                await this._connectLocalDB();  
                await this._loadProductProductPouchDB();
            }
            await super.after_load_server_data();
        }
    
        async _connectLocalDB(){
            console.log(this.config);
            if(this.config.use_pos_data_speed_up){
                this.db.set_save_order_locally(false);                
                // Connect to Products Database  
                const couchdb_url = this.config.couchdb_server_url + this.config.couchdb_products;
                console.log(couchdb_url)                      
                this.productsPouchdb = await new PouchDB(couchdb_url);                
                this.localProducts = await new PouchDB('Products')
                this.localProducts.replicate.from(this.productsPouchdb).then(function(result){
                    console.log("Product Sync Finished");                    
                }).catch(function(err){
                    console.log("Error Product Replication");
                    console.log(err);
                });
                this.db.set_is_pouchdb(true);
                this.db.set_pouchdb_conn(this.localProducts);                
                console.log("Connect to LocalDB");
            }

            if(this.config.save_pos_order){                
                this.remoteOrdersPouchDB = await new PouchDB(this.config.couchdb_server_url + 'p_' + this.config.branch_code + '_' + this.config.code + '_pos_orders');
                this.ordersPouchDB = await new PouchDB('Orders');
                this.db.set_save_order_locally(true);
                this.db.set_save_order_locally_conn(this.ordersPouchDB);
                this.db.set_is_pos_orders_pouchdb_conn(this.remoteOrdersPouchDB);
                this.ordersPouchDB.replicate.to(this.remoteOrdersPouchDB);
            }
        }

        async loadPouchDBProduct(skip){
            console.log('loadPouchDBProduct');
            try {
                var result = await this.localProducts.allDocs({
                  include_docs: true,
                  attachments: true,
                  startkey: 'product',                  
                //   skip: skip,
                //   limit: this.config.limited_products_amount
                });
                return result;
            } catch (err) {
                console.log(err);
            }
        }        

        async _loadProductProductPouchDB(){
            console.log("_loadProductProductPouchDB")
            let skip = 0;            
            var currentRows = 0;            
            var pouchdb_products =  await this.loadPouchDBProduct(skip);                
            var rows = pouchdb_products.rows;            
            var products = [];
            rows.forEach((row) =>  {
                products.push(row.doc);
                // this._loadProductProduct([row.doc]);
            })                        
            await this._loadProductProduct(products);
        }
            
        async _loadProductProduct(products) {        
            console.log(products);
            if(!this.config.use_pos_data_speed_up){
                await super._loadProductProduct(products);
            }else{
                if(products){
                    await super._loadProductProduct(products);
                }
            }
        }    
    }

    Registries.Model.extend(PosGlobalState, PosDataBasePosGlobalState);

    const PosDataBaseOrder = (Order) =>
    class extends Order {
        constructor(obj, options) {
            super(obj, options);            
        }

        // generate_unique_id() {
        //     // Generates a public identification number for the order.
        //     // The generated number must be unique and sequential. They are made 12 digit long
        //     // to fit into EAN-13 barcodes, should it be needed
        //     var result = super.generate_unique_id()
        
        //     function zero_pad(num,size){
        //         var s = ""+num;
        //         while (s.length < size) {
        //             s = "0" + s;
        //         }
        //         return s;
        //     }
        //     return zero_pad(this.pos.pos_session.id,5) + zero_pad(this.sequence_number,4);
        // }
    }

    Registries.Model.extend(Order, PosDataBaseOrder);
    
});