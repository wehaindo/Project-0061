odoo.define('weha_smart_pos_aeon_price.models', function(require){
    'use strict';

    var models = require('point_of_sale.models');
    var { PosCollection, PosModel, PosGlobalState, Order, Orderline, Product } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PriceProduct = (Product) =>
        class extends Product {
            
            get_price(pricelist, quantity, price_extra){
                console.log(pricelist);
                // return super.get_price(pricelist, quantity, price_extra);
                if (pricelist.price_type === 'PDC'){
                    return super.get_price(pricelist, quantity, price_extra);
                }
                if (pricelist.price_type === 'PDCM'){
                    var price = this.get_price_pdcm(pricelist, quantity, price_extra);
                    if(price){
                        return price;
                    }else{
                        var default_pricelist = this.pos.config.pricelist_id;
                        return super.get_price(default_pricelist, quantity, price_extra)
                    }
                } 
            }   
            
            get_price_pdcm(pricelist, quantity, price_extra){
                var self = this;
                var date = moment();
        
                // In case of nested pricelists, it is necessary that all pricelists are made available in
                // the POS. Display a basic alert to the user in this case.
                if (!pricelist) {
                    alert(_t(
                        'An error occurred when loading product prices. ' +
                        'Make sure all pricelists are available in the POS.'
                    ));
                }
        
                var category_ids = [];
                var category = this.categ;
                while (category) {
                    category_ids.push(category.id);
                    category = category.parent;
                }
        
                var pricelist_items = _.filter(self.applicablePricelistItems[pricelist.id], function (item) {
                    return (! item.categ_id || _.contains(category_ids, item.categ_id[0])) &&
                           (! item.date_start || moment.utc(item.date_start).isSameOrBefore(date)) &&
                           (! item.date_end || moment.utc(item.date_end).isSameOrAfter(date));
                });
        
                var price = self.lst_price;
                if (price_extra){
                    price += price_extra;
                }
                var result = _.find(pricelist_items, function (rule) {
                    if (rule.min_quantity && quantity < rule.min_quantity) {                        
                        return false;
                    }
        
                    if (rule.base === 'pricelist') {
                        let base_pricelist = _.find(self.pos.pricelists, function (pricelist) {
                            return pricelist.id === rule.base_pricelist_id[0];
                        });
                        if (base_pricelist) {
                            price = self.get_price(base_pricelist, quantity);
                        }
                    } else if (rule.base === 'standard_price') {
                        price = self.standard_price;
                    }
        
                    if (rule.compute_price === 'fixed') {
                        price = rule.fixed_price;
                        return true;
                    } else if (rule.compute_price === 'percentage') {
                        price = price - (price * (rule.percent_price / 100));
                        return true;
                    } else {
                        var price_limit = price;
                        price = price - (price * (rule.price_discount / 100));
                        if (rule.price_round) {
                            price = round_pr(price, rule.price_round);
                        }
                        if (rule.price_surcharge) {
                            price += rule.price_surcharge;
                        }
                        if (rule.price_min_margin) {
                            price = Math.max(price, price_limit + rule.price_min_margin);
                        }
                        if (rule.price_max_margin) {
                            price = Math.min(price, price_limit + rule.price_max_margin);
                        }
                        return true;
                    }
                    return false;
                });
                if (result){
                    return price;
                }else{
                    return false;
                }
                // This return value has to be rounded with round_di before
                // being used further. Note that this cannot happen here,
                // because it would cause inconsistencies with the backend for
                // pricelist that have base == 'pricelist'.
                
            }s

            get_price_source(pricelist, quantity, price_extra){
                console.log('get_price_source')
                console.log(pricelist);
                // return super.get_price(pricelist, quantity, price_extra);
                if (pricelist.price_type === 'PDC'){
                    return 'pdc';
                }
                if (pricelist.price_type === 'PDCM'){
                    var price = this.get_price_pdcm(pricelist, quantity, price_extra);
                    if(price){
                        return 'pdcm';
                    }else{
                        return 'pdc';
                    }
                }        
            }

            get_list_price(pricelist, quantity, price_extra){
                var default_pricelist = this.pos.config.pricelist_id;
                return super.get_price(default_pricelist, quantity)            
            }

            get_prc(pricelist, quantity, price_extra){
                console.log(pricelist);
                // return super.get_price(pricelist, quantity, price_extra);
                if (pricelist.price_type === 'PDC'){
                    return this.get_prc_no(pricelist, quantity, price_extra);
                }
                if (pricelist.price_type === 'PDCM'){
                    var price = this.get_prc_no(pricelist, quantity, price_extra);
                    if(price){
                        return price;
                    }else{
                        var default_pricelist = this.pos.config.pricelist_id;
                        return super.get_prc_no(default_pricelist, quantity, price_extra)
                    }
                }
            }

            get_prc_no(pricelist, quantity, price_extra){
                var self = this;
                var date = moment();
        
                // In case of nested pricelists, it is necessary that all pricelists are made available in
                // the POS. Display a basic alert to the user in this case.
                if (!pricelist) {
                    alert(_t(
                        'An error occurred when loading product prices. ' +
                        'Make sure all pricelists are available in the POS.'
                    ));
                }
        
                var category_ids = [];
                var category = this.categ;
                while (category) {
                    category_ids.push(category.id);
                    category = category.parent;
                }
        
                var pricelist_items = _.filter(self.applicablePricelistItems[pricelist.id], function (item) {
                    return (! item.categ_id || _.contains(category_ids, item.categ_id[0])) &&
                           (! item.date_start || moment.utc(item.date_start).isSameOrBefore(date)) &&
                           (! item.date_end || moment.utc(item.date_end).isSameOrAfter(date));
                });
        
                var pcr_no = '';
                _.find(pricelist_items, function (rule) {
                    if (rule.min_quantity && quantity < rule.min_quantity) {
                        return false;
                    }
        
                    if (rule.base === 'pricelist') {
                        let base_pricelist = _.find(self.pos.pricelists, function (pricelist) {
                            return pricelist.id === rule.base_pricelist_id[0];});
                        if (base_pricelist) {
                            pcr_no = rule.prc_no;
                        }
                    } else if (rule.base === 'standard_price') {
                        pcr_no = rule.prc_no;
                    }
        
                    if (rule.compute_price === 'fixed') {
                        pcr_no = rule.prc_no;
                        return true;
                    } else if (rule.compute_price === 'percentage') {
                        pcr_no = rule.prc_no;
                        return true;
                    } else {
                        var price_limit = price;
                        price = price - (price * (rule.price_discount / 100));
                        if (rule.price_round) {
                            pcr_no = rule.prc_no;
                        }
                        if (rule.price_surcharge) {
                            pcr_no = rule.prc_no;
                        }
                        if (rule.price_min_margin) {
                            pcr_no = rule.prc_no;
                        }
                        if (rule.price_max_margin) {
                            pcr_no = rule.prc_no;
                        }
                        return true;
                    }
                    return false;
                });
        
                // This return value has to be rounded with round_di before
                // being used further. Note that this cannot happen here,
                // because it would cause inconsistencies with the backend for
                // pricelist that have base == 'pricelist'.
                return pcr_no;                
            }
        }
    
    Registries.Model.extend(Product, PriceProduct);

    const PriceOrder = (Order) =>
    class extends Order {
        constructor(obj, options){
            super(...arguments);
        }
        
        add_product(product, options){
            super.add_product(product, options);
            
            var orderline = this.get_selected_orderline();    
            
            var price_source = product.get_price_source(this.pricelist, 1, {});
            orderline.set_price_source(price_source);

            var list_price = product.get_list_price(this.pricelist, 1, {});   
            orderline.set_list_price(list_price);

            var prc_no = product.get_prc_no(this.pricelist, 1, {});
            console.log('prc_no');
            console.log(prc_no);
            orderline.set_prc_no(prc_no);
        }
        }

    Registries.Model.extend(Order, PriceOrder);

    const PriceOrderLine = (Orderline) =>
        class extends Orderline {
            constructor(obj, options){
                super(...arguments);
                if (options.json) {
                    this.init_from_JSON(options.json);
                    return;
                }
                this.list_price = this.list_price || 0;
                this.price_override_user = this.price_override_user || false;
                this.prc_no = this.prc_no || '';
            }

            clone(){
                const orderline = super.clone(...arguments);
                orderline.list_price = this.list_price;
                orderline.price_override_user = this.price_override_user;
                orderline.prc_no = this.prc_no;
                return orderline;
            }
            
            init_from_JSON(json){
                super.init_from_JSON(...arguments);
                this.list_price = json.list_price;
                this.price_override_user = json.price_override_user;                
                this.prc_no = json.prc_no;
            }

            export_as_JSON(){
                const json = super.export_as_JSON(...arguments);                
                json.list_price = this.list_price;
                json.price_override_user= this.price_override_user;
                json.prc_no = this.prc_no;
                return json;
            }

            set_list_price(list_price){
                this.list_price = list_price;
            }

            get_list_price(){
                return this.list_price;
            }

            set_price_override_user(price_override_user){
                this.price_override_user = price_override_user;
            }

            get_price_override_user(){
                return this.price_override_user;s
            }

            set_prc_no(prc_no){
                this.prc_no = prc_no;
            }

            get_prc_no(){
                return this.prc_no;
            }


        }
        
    Registries.Model.extend(Orderline, PriceOrderLine);

});