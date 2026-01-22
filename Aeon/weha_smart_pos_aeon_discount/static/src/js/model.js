odoo.define('weha_smart_pos_aeon_discount.models', function(require){
    'use strict';

    var models = require('point_of_sale.models');
    var { PosCollection, PosModel, PosGlobalState, Order, Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var field_utils = require('web.field_utils');

    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;


    var discount_orderline_id = 1;
    var discountline_id = 1;

    const DiscountLinePosGlobalState = (PosGlobalState) => 
    class  extends PosGlobalState {
        constructor(obj) {
            super(obj);
        }

        async _processData(loadedData) {
            await super._processData(...arguments);
            this.product_categories = loadedData['product.category'];
            await this.loadProductCategory();
        }
        
        loadProductCategory(){
            this.product_category_by_id = {};
            for(const product_categories of this.product_categories){
                this.product_category_by_id[product_categories.id] = product_categories;
            };
        }
    }

    Registries.Model.extend(PosGlobalState, DiscountLinePosGlobalState);    

   
    const DiscountPosOrder = (Order) => 
    class extends Order {	

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
                    //Calculate Discount Type Fixed
                    console.log('Calculate Discount Type Fixed');
                    console.log(orderLine.get_quantity());
                    console.log(orderLine.get_discount_amount());
                    sum += orderLine.get_quantity() * orderLine.discount_amount;                        
                    console.log(sum);                    
                }
                return sum;
            }, 0), this.pos.currency.rounding);
        }

        apply_member_discount(){
            console.log("Apply Member Day Discount");                    
            var line = this.get_selected_orderline();                                
            var product = line.get_product();            
            var categ_id = product.categ;                            

            // var product_category_id = this.pos.db.get_product_category_by_id(categ_id.id)
            // if(product_category_id){
            //     console.log("Product Category Found");
            //     if(product_category_id.is_member_day_discount === true){
            //         console.log("Product Category Applicable for Member Day")
            //         line.set_discount(product_category_id.member_day_discount_percentage);                                       
            //     }                        
            // } 
            
            var sub_categ_id = product.sub_categ;                            
            if (sub_categ_id){
                var product_sub_category_id = this.pos.db.get_product_sub_category_by_id(sub_categ_id.id)
                if(product_sub_category_id){
                    console.log("Product Sub Category Found");
                    if(product_sub_category_id.is_member_day_discount === true){
                        console.log("Product Sub Category Applicable for Member Day")
                        line.set_discount(product_sub_category_id.member_day_discount_percentage);   
                        // line.set_price_source('member_day');                                    
                        line.set_discount_type('memberday');
                    }                        
                }
            }
            
        }
                
		add_product(product, options){
			super.add_product(product, options);       
            var line = this.get_selected_orderline();
            console.log('Discount Line');
            console.log(line);
            // if(!line.get_promotion()){
            //     if(this.get_aeon_member_day()){                
            //         this.apply_member_discount();
            //     }       
            // }     
            console.log("add_product");
            console.log(line.get_price_source(""));
            if(line.get_price_source("") !== 'mix_and_match'){
                if(this.get_aeon_member_day()){                
                    this.apply_member_discount();
                }     
            }
	    }
        
        // export_for_printing() {
        //     const result = super.export_for_printing(...arguments);
        //     return result;
        // }
	}
	Registries.Model.extend(Order, DiscountPosOrder);
    
    // const DiscountPosOrderline = (Orderline) =>
    // class extends Orderline {
    //     constructor(obj, options) {
    //         super(...arguments);
    //         this.discount_type = this.discount_type || false;
    //     }                

    //     set_discount_type(discount_type){
    //         this.discount_type = discount_type;
    //     }

    //     get_discount_type(){
    //         return this.discount_type;
    //     }

    //     init_from_JSON(json){
    //         super.init_from_JSON(...arguments);
    //         this.discount_type = json.discount_type;
    //     }

    //     clone(){
    //         var orderLine = super.clone();
    //         orderLine.discount_type = this.discount_type;
    //         return orderLine;
    //     }

    //     export_as_JSON(){
    //         var json = super.export_as_JSON();
    //         json.discount_type = this.discount_type;
    //     }

    // }

    // Registries.Model.extend(Orderline, DiscountPosOrderline);
});
