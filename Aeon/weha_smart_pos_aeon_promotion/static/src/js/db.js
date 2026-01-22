odoo.define("weha_smart_pos_aeon_promotion.db", function(require) {
    "use strict";

    var DB = require("point_of_sale.DB");
    var { Product } = require('point_of_sale.models');

    var _super_POSDB = DB.prototype;

    DB.include({
        
        init: function(options){
            var self = this;
            this._super(options);
        },

        set_is_pos_promotions_pouchdb: function(is_pos_promotions_pouch_db){
            this.is_pos_promotions_pouch_db = is_pos_promotions_pouch_db;
        },

        set_pos_promotions_pouchdb_conn: function(conn){
            this.pos_promotions_pouch_db_conn = conn;
        },

    });
    

});