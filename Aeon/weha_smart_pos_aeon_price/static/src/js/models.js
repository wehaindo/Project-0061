odoo.define('weha_smart_pos_aeon_price.models', function(require){
    'use strict';

    var models = require('point_of_sale.models');
    var { PosCollection, PosModel, PosGlobalState, Order, Orderline, Product } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');


    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;

    const PricePosGlobalState = (PosGlobalState) => 
        class extends PosGlobalState {
            compute_all(taxes, price_unit, quantity, currency_rounding, handle_price_include=true) {
                if (this.config.enable_aeon_currency){
                    return super.compute_all(taxes, price_unit, quantity, this.config.aeon_currency_id.rounding, handle_price_include=true)
                }
                return super.compute_all(taxes, price_unit, quantity, currency_rounding, handle_price_include=true)                
            }

            format_currency_no_symbol(amount, precision, currency) {
                if (!currency) {
                    currency = this.currency
                }
                var decimals = currency.decimal_places;
                decimals = 0;
        
                if (precision && this.dp[precision] !== undefined) {
                    decimals = this.dp[precision];
                }
        
                if (typeof amount === 'number') {
                    amount = round_di(amount, decimals).toFixed(decimals);
                    amount = field_utils.format.float(round_di(amount, decimals), {
                        digits: [69, decimals],
                    });
                }
        
                return amount;
            }

        }

    Registries.Model.extend(PosGlobalState, PricePosGlobalState);


    const PriceProduct = (Product) =>
        class extends Product {
            constructor(obj){
                super(obj);
                this.price_source = "list_price";
                this.price_change_no = "";
                this.price_discount = this.price_discount || 0;
            }

            set_price_source(price_source){
                this.price_source = price_source;
            }

            get_price_source(){
                return this.price_source;
            }

            set_price_change_no(price_change_no){
                this.price_change_no = price_change_no;
            }

            get_price_change_no(){
                return this.price_change_no;
            }

            set_price_discount(price_discount){
                this.price_discount = price_discount;
            }

            get_price_discount(){
                return this.price_discount;
            }
                      
            get_price(pricelist, quantity, price_extra){
                var self = this;
                console.log("get_price");
                if (pricelist.price_type === 'PDC'){
                    console.log("Pricelist Type PDC")
                    var price = this.get_price_custom(self, pricelist, quantity, price_extra);                    
                    if(price){
                        console.log("PDC Exist")
                        return price;
                    }else{
                        console.log("No PDC")
                        var default_pricelist = _.find(this.pos.pricelists, function (pricelist) {
                            return pricelist.id === self.pos.config.pricelist_id[0];
                        });                        
                        console.log('default_pricelist');
                        console.log(default_pricelist);
                        return super.get_price(default_pricelist, quantity, price_extra)
                    }
                }else if (pricelist.price_type === 'PDCM'){                    
                    console.log("Pricelist Type PDCM")
                    console.log(pricelist)
                    var price = this.get_price_custom(self, pricelist, quantity, price_extra);
                    console.log("price");
                    console.log(price);
                    if(price){
                        console.log("PDCM Exist")
                        return price;
                    }else{
                        var pdc_pricelist = _.find(this.pos.pricelists, function (pricelist) {
                            return pricelist.price_type ===  'PDC';
                        });
                        if (pdc_pricelist){
                            var price = this.get_price_custom(self, pdc_pricelist, quantity, price_extra);                    
                            if(price){
                                console.log("PDC Exist")
                                return price;
                            }else{
                                console.log("No PDC")
                                var default_pricelist = _.find(this.pos.pricelists, function (pricelist) {
                                    return pricelist.id === self.pos.config.pricelist_id[0];
                                });                        
                                console.log('default_pricelist');
                                console.log(default_pricelist);
                                return super.get_price(default_pricelist, quantity, price_extra)
                            }
                        }else{
                            console.log("No PDCM")
                            var default_pricelist = _.find(this.pos.pricelists, function (pricelist) {
                                return pricelist.id === self.pos.config.pricelist_id[0];
                            });                        
                            console.log('default_pricelist');
                            console.log(default_pricelist);
                            return super.get_price(default_pricelist, quantity, price_extra)
                        }
                    }
                }else{
                    console.log("Pricelist Type Empty")
                    var default_pricelist = _.find(this.pos.pricelists, function (pricelist) {
                        return pricelist.id === self.pos.config.pricelist_id[0];
                    });                        
                    console.log('default_pricelist');
                    console.log(default_pricelist);
                    return super.get_price(default_pricelist, quantity, price_extra)
                }                
            }   

            get_price_custom(product, pricelist, quantity, price_extra){
                var self = this;            
                var date = moment();      
                
                //Clear Price Change Information
                //this.price_source = "";
                //this.price_change_no = "";

                // In case of nested pricelists, it is necessary that all pricelists are made available in
                // the POS. Display a basic alert to the user in this case.
                if (!pricelist) {
                    alert(_t(
                        'An error occurred when loading product prices. ' +
                        'Make sure all pricelists are available in the POS.'
                    ));
                }
        
                var category_ids = [];
                var category = product.categ;
                while (category) {
                    category_ids.push(category.id);
                    category = category.parent;
                }
                
                console.log("applicablePricelistItems");
                console.log(product.applicablePricelistItems);
                var pricelist_items = _.filter(product.applicablePricelistItems[pricelist.id], function (item) {
                    console.log("item");
                    console.log(item);
                    return (! item.categ_id || _.contains(category_ids, item.categ_id[0])
                    ) &&
                           (! item.date_start || moment.utc(item.date_start).isSameOrBefore(date)) &&
                           (! item.date_end || moment.utc(item.date_end).isSameOrAfter(date));
                });
                            
                var price = product.lst_price;    
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
                        product.set_price_source(pricelist.price_type.toLowerCase());
                        product.set_price_change_no(rule.prc_no);                                                                                    
                        price = rule.fixed_price;
                        console.log('discount_price')
                        var discount_price = product.lst_price - price;                        
                        console.log(discount_price);
                        product.set_price_discount(discount_price);                        
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
            }                        
        }
    
    Registries.Model.extend(Product, PriceProduct);

    const PriceOrder = (Order) =>
    class extends Order {
        constructor(obj, options){
            super(...arguments);
        }

        apply_price_change(product, options){
            var orderline = this.get_selected_orderline();                            
            orderline.set_list_price(product.lst_price);
            orderline.set_lst_price(product.lst_price);
            orderline.set_price_source(product.get_price_source());
            orderline.set_prc_no(product.get_price_change_no());
            console.log('apply_price_change');
            console.log(product.get_price_discount());
            if(product.get_price_discount() > 0){
                console.log('set_discount_type');
                orderline.set_discount_type('fixed');
                console.log('set_discount_amount')
                orderline.set_discount_amount(product.get_price_discount());
                console.log('get_discount_amount')
                console.log(orderline.get_discount_amount());
            } 
        }
        
        add_product(product, options){
            super.add_product(product, options);                        
            // Apply Price Change
            this.apply_price_change(product,options);         
        }

        get_total_promo_discount(){
            console.log('get_total_discount')
            const ignored_product_ids = this._get_ignored_product_ids_total_discount()
            console.log(ignored_product_ids)
            return round_pr(this.orderlines.reduce((sum, orderLine) => {
                console.log("orderline");
                console.log(orderLine);
                if (!ignored_product_ids.includes(orderLine.product.id)) {
                    //Calculate Discount Percentage
                    if (orderLine.discount_type === 'fixed'){
                        //Calculate Discount Type Fixed
                        console.log('Calculate Discount Type Fixed');
                        console.log(orderLine.get_quantity());
                        console.log(orderLine.get_discount_amount());
                        sum += orderLine.get_quantity() * orderLine.discount_amount;                        
                        console.log(sum);
                    }
                }
                return sum;
            }, 0), this.pos.currency.rounding);
        }

        get_total_discount() {            
            console.log('get_total_discount')
            const ignored_product_ids = this._get_ignored_product_ids_total_discount()
            console.log(ignored_product_ids)
            return round_pr(this.orderlines.reduce((sum, orderLine) => {
                console.log("orderline");
                console.log(orderLine);
                if (!ignored_product_ids.includes(orderLine.product.id)) {
                    //Calculate Discount Percentage
                    sum += (orderLine.get_unit_price() * (orderLine.get_discount()/100) * orderLine.get_quantity());
                    if (orderLine.display_discount_policy() === 'without_discount'){
                        //Calculate Without Discouont
                        sum += ((orderLine.get_list_price() - orderLine.get_unit_price()) * orderLine.get_quantity());
                    }
                    if (orderLine.discount_type === 'fixed'){
                        //Calculate Discount Type Fixed
                        console.log('Calculate Discount Type Fixed');
                        console.log(orderLine.get_quantity());
                        console.log(orderLine.get_discount_amount());
                        sum += orderLine.get_quantity() * orderLine.discount_amount;                        
                        console.log(sum);
                    }
                }
                return sum;
            }, 0), this.pos.currency.rounding);
        }

        // get_total_tax() {
        //     var sum = super.get_total_tax();
        //     console.log('get_total_tax');
        //     console.log(sum);
        //     sum = parseFloat(round_di(sum, 0).toFixed(0));
        //     console.log(sum);
        //     return sum;
        // }

        // get_total_without_tax() {
        //     var sum = super.get_total_without_tax();
        //     console.log('get_total_without_tax');
        //     console.log(sum);
        //     sum = parseFloat(round_di(sum, 0).toFixed(0));
        //     console.log(sum);
        //     return sum            
        // }
    }

    Registries.Model.extend(Order, PriceOrder);

    const PriceOrderLine = (Orderline) =>
        class extends Orderline {
            constructor(obj, options){
                super(...arguments);
                var self = this;
                self.original_prices = options.original_prices || false
                if (options.json) {
                    this.init_from_JSON(options.json);
                    var orderline_json = options.json
                    if (orderline_json.original_price)
                        self.original_prices = orderline_json.original_prices;                    
                }         
                this.list_price = this.list_price || 0;
                this.price_override_user = this.price_override_user || false;
                this.price_override_reason = this.price_override_reason || false;
                this.prc_no = this.prc_no || '';
                this.price_source = this.price_source || '';
                this.discount_type = this.discount_type || '';      
                this.discount_amount = this.discount_amount || 0; //For fixed discount_type                                      
            }

            clone(){
                const orderline = super.clone(...arguments);
                orderline.list_price = this.list_price;
                orderline.price_override_user = this.price_override_user;
                orderline.price_override_reason = this.price_override_reason;
                orderline.prc_no = this.prc_no;
                orderline.price_source = this.price_source
                orderline.discount_type = this.discount_type;
                orderline.discount_amount = this.discount_amount;
                return orderline;
            }
            
            init_from_JSON(json){
                super.init_from_JSON(...arguments);
                this.list_price = json.list_price;
                this.price_override_user = json.price_override_user; 
                this.price_override_reason = json.price_override_reason;               
                this.prc_no = json.prc_no;
                this.price_source = json.price_source;
                this.discount_type = json.discount_type;
                this.discount_amount = json.discount_amount;
            }

            export_as_JSON(){
                const json = super.export_as_JSON(...arguments);                
                json.list_price = this.list_price;
                json.price_override_user= this.price_override_user;
                json.price_override_reason = this.price_override_reason;
                json.prc_no = this.prc_no;
                json.price_source = this.price_source;
                json.discount_type = this.discount_type;
                json.discount_amount = this.discount_amount;
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

            set_price_override_reason(price_override_reason){
                this.price_override_reason = price_override_reason;
            }

            get_price_override_reason(){
                return this.price_override_reason;
            }

            set_prc_no(prc_no){
                this.prc_no = prc_no;
            }

            get_prc_no(){
                return this.prc_no;
            }

            set_price_source(price_source){
                this.price_source = price_source;
            }

            get_price_source(){
                return this.price_source;
            }

            set_discount_type(discount_type){
                this.discount_type = discount_type;
            }

            get_discount_type(){
                return this.discount_type;
            }

            set_discount_amount(discount_amount){
                this.discount_amount = discount_amount;
            }

            get_discount_amount(){
                return this.discount_amount;
            }       

            get_original_price(){
                return this.original_prices;
            }

            // //For Receipt
            // get_price_without_tax(){
            //     var priceWithoutTax = super.get_price_without_tax()
            //     console.log('get_price_without_tax');
            //     console.log(priceWithoutTax);
            //     priceWithoutTax = parseFloat(round_di(priceWithoutTax, 0).toFixed(0));
            //     console.log(priceWithoutTax);
            //     return priceWithoutTax;                    
            // }
            
            // //For Receipt
            // get_tax(){
            //     var tax = super.get_tax()
            //     console.log('get_tax');
            //     console.log(tax);
            //     tax = parseFloat(round_di(tax, 0).toFixed(0));
            //     console.log(tax);
            //     return tax;                
            // }

            // get_all_prices(qty = this.get_quantity()){
            //     var price_unit = this.get_unit_price() * (1.0 - (this.get_discount() / 100.0));
            //     var taxtotal = 0;
        
            //     var product =  this.get_product();
            //     var taxes_ids = this.tax_ids || product.taxes_id;
            //     taxes_ids = _.filter(taxes_ids, t => t in this.pos.taxes_by_id);
            //     var taxdetail = {};
            //     var product_taxes = this.pos.get_taxes_after_fp(taxes_ids, this.order.fiscal_position);
        
            //     var all_taxes = this.compute_all(product_taxes, price_unit, qty, 1);
            //     var all_taxes_before_discount = this.compute_all(product_taxes, this.get_unit_price(), qty, this.pos.currency.rounding);
            //     _(all_taxes.taxes).each(function(tax) {
            //         taxtotal += tax.amount;
            //         taxdetail[tax.id] = tax.amount;
            //     });
        
            //     return {
            //         "priceWithTax": all_taxes.total_included,
            //         "priceWithoutTax": all_taxes.total_excluded,
            //         "priceWithTaxBeforeDiscount": all_taxes_before_discount.total_included,
            //         "tax": taxtotal,
            //         "taxDetails": taxdetail,
            //     };
            // }

            export_for_printing(){
                var self=this;
                const json = super.export_for_printing(...arguments);
                console.log(json);
                json.discount_type = self.get_discount_type();
                json.discount_amount = self.get_discount_amount();    
                json.price_lst = self.product.lst_price;
                json.original_prices = self.product.lst_price * json.quantity;      
                json.price_source = self.get_price_source();  
                json.prc_no = self.get_prc_no();
                json.promotion_code = '';
                json.promotion_description = '';    
                return json;
            }
        }
        
    Registries.Model.extend(Orderline, PriceOrderLine);
    
});