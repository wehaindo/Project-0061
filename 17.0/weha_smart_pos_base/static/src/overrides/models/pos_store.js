/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { onWillStart } from "@odoo/owl";
import { loadJS } from "@web/core/assets";


patch(PosStore.prototype, {

    async setup(){
        await super.setup(...arguments);
        // onWillStart(async () => {
        //     await loadJS("/weha_smart_pos_base/static/lib/js/pouchdb-8.0.1.min.js");
        // });
    },

    async logoutPos() {
        window.location = '/pos/login/' + this.config.pos_config_code;
    },
    // Multiple barcode
    async _loadProductBarcode(loadedData){
        var self = this;
        console.log('loadProductBarcode');
        var product_template_barcodes = loadedData['product.template.barcode'];                          
        product_template_barcodes.forEach(function(product_barcode){
            var product = self.db.product_by_id[product_barcode['product_product_id']]
            if(product){
                self.db.product_by_barcode[product_barcode['barcode']] = product;                
            }
        })
        console.log(this.db.product_by_barcode);
    },

    //Support Channel
    async _loadDiscussChannel(loadedData){
        this.discuss_channels = loadedData['discuss.channel'];
    },

    //POS Multi UOM
    async _loadPosProductMultiUom(loadedData){
        this.em_uom_list = loadedData['pos.product.multi.uom'];
    },

    //@override
    async _processData(loadedData) {
        await super._processData(...arguments);
        if (this.config.use_store_access_rights) {
            this.hr_employee_supervisors = loadedData['hr.employee.supervisor'];
            this.hr_employee_supervisor_by_id = loadedData['hr.employee.supervisor.by.id'];                
            this.hr_employee_supervisor_by_rfid = loadedData['hr.employee.supervisor.by.rfid'];                
        }
        await this._loadProductBarcode(loadedData);
        await this._loadDiscussChannel(loadedData);
        await this._connectLocalDB();

        // Pos Promotion
        this.pos_promotions = loadedData['pos.promotion'];
        this.pos_conditions = loadedData['pos.conditions'];
        this.pos_partial_quantity_fixed_prices = loadedData['partial.quantity.fixed.price'];
        this.quantity_fixed_prices = loadedData['quantity.fixed.price'];
        this.get_discount = loadedData['get.discount'];
        this.pos_get_qty_discount = loadedData['quantity.discount'];
        this.pos_get_qty_discount_amt = loadedData['quantity.discount.amt'];
        this.pos_fixed_price_multi_prods = loadedData['fixed.price.multi.products']; 
        this.pos_free_product_multi_prods = loadedData['free.product.multi.products']; 
        this.pos_discount_multi_prods = loadedData['discount.multi.products']; 
        this.pos_discount_multi_category = loadedData['discount.multi.categories']; 
        this.pos_price_combination_products = loadedData['price.combination.products'];

        await this.loadPosPromotion();                
        await this.loadPosCondition();
        await this.loadPartialQuantityFixedPrice();
        await this.loadQuantityFixedPrice();
        await this.loadGetDiscount();
        await this.loadQuantityDiscount();
        await this.loadQuantityDiscountAmt();
        await this.loadFixedPriceMultiProducts();
        await this.loadFreeProductMultiProducts();
        // await this.loadDiscountMultiProducts();
        // await this.loadDiscountMultiCategories();
        // await this.loadPriceCombinationProducts();
    },

    async _connectLocalDB(){
        if (this.config.is_save_pos_order_to_localdb){
            this.ordersPouchDB = await new PouchDB('Orders');
            this.db.set_is_save_order_to_local_db(true);
            this.db.set_pos_orders_pouchdb_conn(this.ordersPouchDB);
        }else{
            this.db.set_is_save_order_to_local_db(false);
        }
        // if(this.config.save_pos_order){                
        //     this.remoteOrdersPouchDB = await new PouchDB(this.config.couchdb_server_url + 'p_' + this.config.branch_code + '_' + this.config.code + '_pos_orders');
        //     this.ordersPouchDB = await new PouchDB('Orders');
        //     this.db.set_save_order_locally(true);
        //     this.db.set_save_order_locally_conn(this.ordersPouchDB);
        //     this.db.set_is_pos_orders_pouchdb_conn(this.remoteOrdersPouchDB);
        //     this.ordersPouchDB.replicate.to(this.remoteOrdersPouchDB);
        // }
    },
    // Pos Promotion
    loadPosPromotion(){
        console.log('loadPosPromotion');
        this.pos_promotions_by_id = {};
        for(const pos_promotions of this.pos_promotions){
            this.pos_promotions_by_id[pos_promotions.id] = pos_promotions;
        };
        console.log(this.pos_promotions_by_id);
    },

    loadPosCondition(){
        console.log('loadPosConditions');
        this.pos_conditions_by_id = {};
        for(const pos_condition of this.pos_conditions){
            this.pos_conditions_by_id[pos_condition.id] = pos_condition;
        };
    },

    loadPartialQuantityFixedPrice(){
        this.pos_partial_quantity_fixed_price_by_id = {};
        for(const pos_partial_quantity_fixed_price of this.pos_partial_quantity_fixed_prices){
            this.pos_partial_quantity_fixed_price_by_id[pos_partial_quantity_fixed_price.id] = pos_partial_quantity_fixed_price;
        };
    },

    loadQuantityFixedPrice(){
        this.quantity_fixed_price_by_id = {};
        for(const quantity_fixed_price of this.quantity_fixed_prices){
            this.quantity_fixed_price_by_id[quantity_fixed_price.id] = quantity_fixed_price;
        };
    },

    loadGetDiscount(){
        this.get_discount_by_id = {};
        for(const get_discount of this.get_discount){
            this.get_discount_by_id[get_discount.id] = get_discount;
        };
    },

    loadQuantityDiscount(){
        this.quantity_discount_by_id = {};
        for(const pos_get_qty_discount of this.pos_get_qty_discount){
            this.get_discount_by_id[pos_get_qty_discount.id] = pos_get_qty_discount;
        };
    },

    loadQuantityDiscountAmt(){
        this.quantity_discount_amt_by_id = {};
        for(const pos_get_qty_discount_amt of this.pos_get_qty_discount_amt){
            this.get_discount_amt_by_id[pos_get_qty_discount_amt.id] = pos_get_qty_discount_amt;
        };
    },

    loadFixedPriceMultiProducts(){
        this.pos_fixed_price_multi_prods_by_id = {};
        for(const prod of this.pos_fixed_price_multi_prods){
            this.pos_fixed_price_multi_prods_by_id[prod.id] = prod;
        };
    },

    loadFreeProductMultiProducts(){
        this.pos_free_product_multi_prods_by_id = {};
        for(const prod of this.pos_free_product_multi_prods){
            this.pos_free_product_multi_prods_by_id[prod.id] = prod;
        };
    },

    loadDiscountMultiProducts(){
        this.pos_discount_multi_prods_by_id = {};
        for(const prod of this.pos_discount_multi_prods){
            this.pos_discount_multi_prods_by_id[prod.id] = prod;
        };
    },

    loadDiscountMultiCategories(){
        this.pos_discount_multi_category_by_id = {};
        for(const pos_discount_multi_category of this.pos_discount_multi_category){
            this.pos_discount_multi_category_by_id[pos_discount_multi_category.id] = pos_discount_multi_category;
        };
    },

    loadDiscountAbovePrice(){
        this.pos_discount_above_price = pos_discount_above_price;
    },

    loadPriceCombinationProducts(){
        this.pos_price_combination_products_by_id = {};
        for(const prod of this.pos_price_combination_products){
            this.pos_price_combination_products_by_id[prod.id] = prod;
        };                
        console.log('loadPriceCombinationProducts');
        console.log(this.pos_price_combination_products);
        console.log(this.pos_price_combination_products_by_id);
    },
});