odoo.define('weha_smart_pos_aeon_pos_data.models', function(require){
    "use strict";

    var models = require('point_of_sale.models');
    var { PosCollection, PosModel, PosGlobalState, Order, Orderline, Product } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');


    const AeonPosDataPosGlobalState = (PosGlobalState) => 
    class  extends PosGlobalState {
        constructor(obj) {
            super(obj);
        }

        async _processData(loadedData) {
            console.log("_processData");
            console.log(loadedData);
            super._processData(loadedData);
            this.db.add_product_categories(loadedData['product.category']);
            this.db.add_product_subcategories(loadedData['product.sub.category']);
        }

        async load_orders(){
            console.log("Load Order From POS Data");
            await super.load_orders();
        }       
        
        async after_load_server_data(){
            var self = this;
            if(this.config.use_pos_data_speed_up){
                this.db.set_pos(this.pos);
                await this.db.set_pos_global_state(this);
                await this._connectLocalDB();  
                // await this._loadProductCategoryPouchDB();                              
                await this._loadProductPriceListItemPouchDB();                
                await this._loadProductProductPouchDB();
                await this._loadProductBarcodePouchDB();
                // if(!this.config.direct_pos_data_local_products_db){
                //     await this._loadProductProductPouchDB();
                // }
            }
            await super.after_load_server_data();
        }
    
        async _connectLocalDB(){
            console.log(this.config);
            if(this.config.use_pos_data_speed_up){
                this.db.set_save_order_locally(false);                
                // Connect to Products Database                        
                this.productsPouchdb = await new PouchDB(this.config.couchdb_server_url + this.config.couchdb_products);                
                this.localProducts = await new PouchDB('Products')
                this.localProducts.replicate.from(this.productsPouchdb).then(function(result){
                    console.log("Product Sync Finished");                    
                }).catch(function(err){
                    console.log(err);
                });
                this.db.set_is_pouchdb(true);
                this.db.set_pouchdb_conn(this.localProducts);

                // Connect to Product Barcode Database                        
                this.productBarcodesPouchdb = await new PouchDB(this.config.couchdb_server_url + this.config.couchdb_product_barcodes);                
                this.localProductBarcodes = await new PouchDB('ProductBarcodes')
                this.localProductBarcodes.replicate.from(this.productBarcodesPouchdb).then(function (result) {
                    console.log("Product Barcode Sync Finished");
                }).catch(function(err){
                    console.log(err);
                });
                this.db.set_is_product_barcode_pouchdb(true);
                this.db.set_product_barcode_pouchdb_conn(this.localProductBarcodes);

                // Connect to Products Categories Database
                this.productCategoriesPouchdb = await new PouchDB(this.config.couchdb_server_url + this.config.couchdb_product_categories);                
                this.localProductCategoriesPouchdb = await new PouchDB('ProductCategories')            
                this.localProductCategoriesPouchdb.replicate.from(this.productCategoriesPouchdb)
                this.db.set_is_product_category_pouchdb(true);
                this.db.set_product_category_pouchdb_conn(this.localProductCategoriesPouchdb);

                // Connect to Product Pricelist Item
                this.productPricelistItemsPouchdb = await new PouchDB(this.config.couchdb_server_url + this.config.couchdb_product_pricelist_items);                
                this.localProductPricelistItemsPouchdb = await new PouchDB('PricelistItems')                
                this.localProductPricelistItemsPouchdb.replicate.from(this.productPricelistItemsPouchdb)
                this.db.set_is_product_pricelist_item_pouchdb(true);
                this.db.set_product_pricelist_item_pouchdb_conn(this.localProductPricelistItemsPouchdb);

                
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

        async loadPouchDBProductBarcode(skip){
            console.log('loadPouchDBProductBarcode');
            try {
                var result = await this.localProductBarcodes.allDocs({
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

        async loadPouchDBProductCategory(){
            try {
                var result = await this.productCategoriesPouchdb.allDocs({
                  include_docs: true,
                  attachments: trues,
                  startkey: 'productcategory',
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
            })                        
            await this._loadProductProduct(products);
        }
    
        async _loadProductBarcodePouchDB(){
            var self = this;
            console.log("_loadProductBarcodePouchDB")
            let skip = 0;            
            var currentRows = 0;            
            var pouchdb_products =  await this.loadPouchDBProductBarcode(skip);                
            var rows = pouchdb_products.rows;            
            var products = [];
            rows.forEach((row) =>  {
                products.push(row.doc);
            })                  
            products.forEach( function (product) {
                var prd = self.db.product_by_id[product.id];
                self.db.product_by_barcode[product.barcode] = prd;               
            });
            // var test_product_barcode = this.db.product_by_barcode[products[0].barcode];
            // await this._loadProductProduct(products);
        }

        async _loadProductProduct(products) {        
            if(!this.config.use_pos_data_speed_up){
                await super._loadProductProduct(products);
            }else{
                if(products){
                    await super._loadProductProduct(products);
                }
            }
        }

        async _loadProductCategoryPouchDB(){
            var pouchdb_product_categories = await this.loadPouchDBProductCategory();
            console.log('_loadProductCategoryPouchDB');
            console.log(pouchdb_product_categories);   
            var rows = pouchdb_product_categories.rows;    
            console.log(rows);
            const modelProductCategories = rows.map(row => {
                return row.doc;
            });
            // this.db.add_categories(modelProductCategories);
        }
 
        async loadPouchDBProductPricelistItem(){
            try {
                var result = await this.localProductPricelistItemsPouchdb.allDocs({
                  include_docs: true,
                  attachments: true,
                  startkey: 'productpricelistitem',
                });
                return result;
            } catch (err) {
                console.log(err);
            }
        }

        async _loadProductPriceListItemPouchDB(){
            var pouchdb_product_pricelist_items = await this.loadPouchDBProductPricelistItem();
            console.log('Start _loadProductPriceListItemPouchDB');            
            var rows = pouchdb_product_pricelist_items.rows;    
            console.log(rows);
            await this.pricelists.forEach(pricelist => {                
                rows.map(row => {
                    const doc = row.doc;
                    if (pricelist.id === doc.pricelist_id[0]){
                        pricelist['items'].push(doc);    
                    }
                });
                console.log('pricelist');
                console.log(pricelist.name)
                console.log('pricelist items');
                console.log(pricelist.items)
            });
            console.log("Finish _loadProductPriceListItemPouchDB")            
        }
            
        async _get_local_product_by_barcode(barcode){
            var self = this;
            let promise = new Promise(function (resolve, reject){                     
                self.localProducts.createIndex({
                    index: {
                        fields:['barcode']
                    }
                }).then(function (){
                    self.localProducts.find({
                        selector: {
                            'barcode': barcode,
                        }
                    }).then((result) => {
                        var product = result['docs'][0];  
                        var products = []
                        products.push(product)         
                        resolve(products);                     
                        // await self._loadProductProduct(products);                            
                    }).catch(function(err){
                        reject(err)
                    })
                }).catch(function(err){
                    reject(err)
                })                
            });
            let result = await promise;
            return result;
        }

        async get_local_product_by_barcode(barcode){
            console.log('get_local_product_by_barcode');
            var self = this;
            let product = false;
            if(!product){
                await this._get_local_product_by_barcode(barcode).then(function(products){
                    console.log('_loadProductProduct');
                    self._loadProductProduct(products)
                })                
            }
        }
    }

    Registries.Model.extend(PosGlobalState, AeonPosDataPosGlobalState);

    const AeonPosDataOrder = (Order) =>
    class extends Order {
        constructor(obj, options) {
            super(obj, options);            
        }

        generate_unique_id() {
            // Generates a public identification number for the order.
            // The generated number must be unique and sequential. They are made 12 digit long
            // to fit into EAN-13 barcodes, should it be needed
            var result = super.generate_unique_id()
        
            function zero_pad(num,size){
                var s = ""+num;
                while (s.length < size) {
                    s = "0" + s;
                }
                return s;
            }
            return zero_pad(this.pos.pos_session.id,5) + zero_pad(this.sequence_number,4);
            // return (String(this.pos.pos_session.id).slice(-4) + zero_pad(this.sequence_number,4));

        }
    }

    Registries.Model.extend(Order, AeonPosDataOrder);


    // const AeonPosDataOrderline = (Orderline) => 
    // class  extends Orderline {
    //     constructor(obj) {
    //         super(obj);            
    //     }

    //     get_product(){
    //         console.log("Get Product")
    //         var product = super.get_product();
    //         console.log(product);
    //         return product;
    //     }
    // }

    // Registries.Model.extend(Orderline, AeonPosDataOrderline);

});