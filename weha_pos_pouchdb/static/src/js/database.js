odoo.define('pos_pouchdb.database', function (require) {
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var _t = core._t;

    
    //Pouch Database
    var dbposorders = new PouchDB('posorders', { skip_setup: true });
    var remotePosOrders = 'http://admin:admin123@128.199.175.43:5984/posorders';
    console.log('Create Pos Orders Database');

    var db = require('point_of_sale.DB');
    var _super_db = db.prototype;
    
    //function syncError() {
    //    console.log("error");
    //}
    
    //function sync() {
        //syncDom.setAttribute('data-sync-state', 'syncing');
    //    var opts = {live: true};
    //    dbposorders.replicate.to(remotePosOrders, opts, syncError);
    //    dbposorders.replicate.from(remotePosOrders, opts, syncError);
    //}

    db.include({
        init: function (options) {
            var self = this;
            this._super(options);
            console.log(self);
            if (remotePosOrders) {
                this.sync(true);
            }
        },
        sync: function(live){
            var opts = {live: true};
            dbposorders.replicate.to(remotePosOrders, opts, this.syncError);
            dbposorders.replicate.from(remotePosOrders, opts, this.syncError);
        },
        syncError: function(){
            console.log("error");
        },
        save: function(store,data){
            this._super(store,data);
            console.log('Save Pos Order to PouchDB');
            console.log(store);
            if( store === 'orders'){
                console.log(data[0]['data']);
                order = data[0]['data']
                order['_id'] = order['uid'];
                dbposorders.put(order, function callback(err, result) {
                    if (!err) {
                        console.log('Successfully posted a pos order!');
                    }else{
                        console.log(err);
                    }
                });
            }
        },
    });
});
