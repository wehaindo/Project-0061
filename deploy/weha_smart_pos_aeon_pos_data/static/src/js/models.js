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

        async load_orders(){
            console.log("Load Order From POS Data");
            await super.load_orders();
        }       
        
        async after_load_server_data(){
            if(this.config.use_pos_data_speed_up){
                await this.connectToCouchDb();
                await this._loadProductPriceListItemPouchDB();
                await this._loadProductProductPouchDB();
                await this._loadProductCategoryPouchDB();    
            }
            await super.after_load_server_data();
        }
    
        async connectToCouchDb(){
            console.log(this.config);
            if(this.config.use_pos_data_speed_up){
                this.db.set_save_order_locally(false);
                // Connect to Products Database
                this.productsPouchdb = await new PouchDB('http://admin:pelang1@localhost:5984/products');                
                this.db.set_is_pouchdb(true);
                this.db.set_pouchdb_conn(this.productsPouchdb);
                // Connect to Products Categories Database
                this.productCategoriesPouchdb = await new PouchDB('http://admin:pelang1@localhost:5984/product_categories');                
                this.db.set_is_product_category_pouchdb(true);
                this.db.set_product_category_pouchdb_conn(this.productCategoriesPouchdb);
                // Connect to Product Pricelist Item
                this.productPricelistItemsPouchdb = await new PouchDB('http://admin:pelang1@localhost:5984/product_pricelist_items');                
                this.db.set_is_product_pricelist_item_pouchdb(true);
                this.db.set_product_pricelist_item_pouchdb_conn(this.productPricelistItemsPouchdb);
                if(this.config.save_pos_order){
                    // Connect Orders Database
                    this.ordersPouchDB = await new PouchDB('http://admin:pelang1@localhost:5984/orders');
                    this.db.set_save_order_locally(true);
                    this.db.set_save_order_locally_conn(this.ordersPouchDB);
                }
                console.log("Connect to couchdb");
            }
        }

        async loadPouchDBProduct(){
            try {
                var result = await this.productsPouchdb.allDocs({
                  include_docs: true,
                  attachments: true,
                  startkey: 'product',
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
                  attachments: true,
                  startkey: 'productcategory',
                });
                return result;
            } catch (err) {
                console.log(err);
            }
        }

        async _loadProductProductPouchDB(){
            var pouchdb_products = await this.loadPouchDBProduct();
            console.log('_loadProductProduct');
            console.log(pouchdb_products);        
            var rows = pouchdb_products.rows;
            console.log(rows);
    
            const productMap = {};
            const productTemplateMap = {};
    
            const modelProducts = rows.map(row => {
                var product = row.doc;
                product.pos = this;
                product.applicablePricelistItems = {};
                productMap[product.id] = product;
                productTemplateMap[product.product_tmpl_id[0]] = (productTemplateMap[product.product_tmpl_id[0]] || []).concat(product);
                return Product.create(product);
            });
    
            for (let pricelist of this.pricelists) {
                for (const pricelistItem of pricelist.items) {
                    if (pricelistItem.product_id) {
                        let product_id = pricelistItem.product_id[0];
                        let correspondingProduct = productMap[product_id];
                        if (correspondingProduct) {
                            this._assignApplicableItems(pricelist, correspondingProduct, pricelistItem);
                        }
                    }
                    else if (pricelistItem.product_tmpl_id) {
                        let product_tmpl_id = pricelistItem.product_tmpl_id[0];
                        let correspondingProducts = productTemplateMap[product_tmpl_id];
                        for (let correspondingProduct of (correspondingProducts || [])) {
                            this._assignApplicableItems(pricelist, correspondingProduct, pricelistItem);
                        }
                    }
                    else 
                    {
                        for (const correspondingProduct of modelProducts) {
                            this._assignApplicableItems(pricelist, correspondingProduct, pricelistItem);
                        }
                    }
                }
            }
            this.db.add_products(modelProducts)                        
        }
    
        async _loadProductProduct(products) {        
            if(!this.config.use_pos_data_speed_up){
                console.log('_loadProductProduct Default Odoo')
                await super._loadProductProduct(products);
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
            // var result = await this.productPricelistItemsPouchdb.find(
            //     {
            //         "pricelist_id": {
            //             "$all": [
            //                6
            //             ]
            //         }
            //     }
            // )

            // return result;
            try {
                var result = await this.productPricelistItemsPouchdb.allDocs({
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
            console.log('_loadProductPriceListItemPouchDB');
            console.log(pouchdb_product_pricelist_items);   
            var rows = pouchdb_product_pricelist_items.rows;    
            console.log(rows);
            this.pricelists.forEach(pricelist => {
                console.log('pricelist');
                console.log(pricelist);
                // const modelProductPricelistItems = rows.map(row => {

                rows.map(row => {
                    console.log('row');
                    console.log(row);
                    const doc = row.doc;
                    console.log('doc');
                    console.log(doc);
                    console.log('pricelist_id');
                    console.log(doc.pricelist_id);
                    if (pricelist.id === doc.pricelist_id[0]){
                        pricelist['items'].push(doc);    
                    }
                });
                // pricelist['items'].push.apply(pricelist['items'], modelProductPricelistItems);
            });
            console.log('pricelists');
            console.log(this.pricelists);
            // const modelProductPricelistItems = rows.map(row => {
            //     return row.doc;
            // });
            
            // this.db.add_categories(modelProductCategories);
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