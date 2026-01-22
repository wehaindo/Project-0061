odoo.define('pos_pouchdb.pouchDB', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;

    console.log('Create PouchDB Database');
    
    //Pouch Database
    var dbproducts = new PouchDB('posorders', { skip_setup: true });
    //var remotePosOrders = 'http://admin:admin123@128.199.175.43:5984/posorders';



    //var todo = {
    //    _id: new Date().toISOString(),
    //    title: "Testing",
    //    completed: false
    //};

    //function addProduct(product){
    //    console.log("Add product to db");
    //    dbproducts.put(product, function callback(err, result) {
    //        if (!err) {
    //        console.log('Successfully posted a todo!');
    //        }
    //    });
    //}

    //var db = new PouchDB('odoo_pos_product', { skip_setup: true });
    //var product = {
    //    _id: 1,
    //    name: "Fanta",
    //    price: 7500,
    //    stock: 15
    //}

    //db.put(product, function callback(err, result) {
    //    if (!err) {
    //      console.log('Successfully posted a product!');
    //    }
    //});

    /* 
    var posmodel_super = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        load_server_data: function () {
            var self = this;

            var product_index = _.findIndex(this.models, function (model) {
                return model.model === "product.product";
            });

            var product_model = self.models[product_index];

            // We don't want to load product.product the normal
            // uncached way, so get rid of it.
            if (product_index !== -1) {
                this.models.splice(product_index, 1);
            }
            return posmodel_super.load_server_data.apply(this, arguments).then(function () {
                var dbproducts = new PouchDB('products', { skip_setup: true });
                var remoteCouch = 'http://admin:admin123@128.199.175.43:5984/products';

                function syncError() {
                    console.log("error");
                }

                function sync() {
                    //syncDom.setAttribute('data-sync-state', 'syncing');
                    var opts = {live: true};
                    dbproducts.replicate.to(remoteCouch, opts, syncError);
                    dbproducts.replicate.from(remoteCouch, opts, syncError);
                }
                
                if (remoteCouch) {
                    self.chrome.loading_message(_t('Loading') + ' product.product', 1);
                    sync()
                    dbproducts.allDocs({include_docs: true}, function(err, docs) {
                        if (err) {
                        return console.log(err);
                        } else {
                        //console.log (docs.rows);
                            self.db.add_products(_.map(docs.rows, function (row) {
                                console.log(row.doc);
                                var product = row.doc;
                                product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
                                return new models.Product({}, product);
                            }));
                        }
                    });
                        //dbproducts.allDocs({
                        //    include_docs: true,
                        //    attachments: true
                        //}).then(function (result) {
                            // handle result
                        //    console.log("add_products");
                        //    self.db.add_products(_.map(result, function (product) {
                        //        product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
                        //        return new models.Product({}, product);
                        //    }));
                        //}).catch(function (err) {
                        //    console.log(err);
                        //});
                }
            // Give both the fields and domain to pos_cache in the
            // backend. This way we don't have to hardcode these
            // values in the backend and they automatically stay in
            // sync with whatever is defined (and maybe extended by
            // other modules) in js.
            //var product_fields =  typeof product_model.fields === 'function'  ? product_model.fields(self)  : product_model.fields;
            //var product_domain =  typeof product_model.domain === 'function'  ? product_model.domain(self)  : product_model.domain;
            //var records = rpc.query({
            //          model: 'product.product',
            //          method: 'search_read',
            //          fields: ['name']
            //      });
                
                //return records.then(function (products) {
                //    self.db.add_products(_.map(products, function (product) {
                //        product.categ = _.findWhere(self.product_categories, {'id': product.categ_id[0]});
                //        return new models.Product({}, product);
                //    }));
                    //for (var product of products) {
                    //    console.log(product);
                    //    //this.addProduct(product);
                    //}
                //});
            });
        },
});

*/
    //models.load_models([
    //    {
    //        label: 'products',
    //       condition: function (self) {
    //            return true;
    //        },
    //        loaded: function (self) {
    //            var status = new $.Deferred();
    //            return status;
    //        },
    //    },
    //]);


    
});