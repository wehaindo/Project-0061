odoo.define('weha_smart_pos_aeon_discount.models', function(require){
    'use strict';

    var models = require('point_of_sale.models');
    var { PosCollection, PosModel, PosGlobalState, Order, Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    var discount_orderline_id = 1;
    var discountline_id = 1;

    const DiscountLine = (PosModel) => 
    class DiscountLine extends PosModel{ 
        constructor(obj, options){
            super(obj);           
            this.orderline = options.orderline; 
            if (options.json) {
                try {
                    this.init_from_JSON(options.json);
                } catch(_error) {
                    console.error('ERROR: Init ');
                }
                return;
            }
            this.id = discountline_id++;
        }
    
        init_from_JSON(json) {
            this.discount_type = json.discount_type;
            this.discount_percentage = json.discount_percentage;
            this.discount_fixed = json.discount_fixed;
            this.discount_source = json.discount_source;
            this.id = json.id ? json.id : discountline_id++;
            discountline_id = Math.max(this.id+1,discountline_id);
        }
       
        set_discount_source(discount_source){
            this.discount_source = discount_source;
        }

        get_discount_source(){
            return this.discount_source;
        }

        set_discount_type(discount_type){
            this.discount_type = discount_type || null;
        }

        get_discount_type(){
            return this.discount_type;
        }
        
        set_discount_percentage(discount_percentage){
            this.discount_percentage = discount_percentage || 0;
        }

        get_discount_percentage(){
            return this.discount_percentage;
        }

        set_discount_fixed(discount_fixed){
            this.discount_fixed = discount_fixed || 0;
        }

        get_discount_fixed(){
            return this.discount_fixed;
        }

        get_line_discount_str(){
            if(this.discount_type == 'percentage'){
                return "Discount with " + this.discount_type + ' for ' + this.discount_percentage;
            }else{
                return "Discount with " + this.discount_type + ' for ' + this.discount_fixed;
            }
        }

        export_as_JSON(){
            return {
                discount_type: this.get_discount_type(),   
                discount_percentage: this.get_discount_percentage(),
                discount_fixed: this.get_discount_fixed(),
                discount_source: this.get_discount_source(),
                discount_str: this.get_line_discount_str(),
                id: this.id
            };
        }
    }

    Registries.Model.add(DiscountLine);

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

    

    const DiscountOrderLine = (Orderline) => 
    class extends Orderline { 
        constructor() {
            super(...arguments);   
            // this.pos_order_line_discounts = this.pos_order_line_discounts || new PosCollection();                     
            this.pos_order_line_discounts = this.pos_order_line_discounts;                     
        }
        
        add_line_discount(line_discount){
            line_discount.orderline = this;
            if(this.pos_order_line_discounts){
                this.pos_order_line_discounts.add(line_discount);
            }else{
                this.pos_order_line_discounts = new PosCollection();
                this.pos_order_line_discounts.add(line_discount);
            }
        }

        get_line_discounts(){
            return this.pos_order_line_discounts;
        }

        async get_line_total_discounts(){
            var line_discounts = this.get_line_discounts();
            var discount = 0;
            await line_discounts.map((obj, i) => {
                if(discount == 0){
                    discount = obj.get_discount_percentage();
                }else{
                    discount = discount * obj.get_discount_percentage();
                }
            });
            return discount;
        }

        clone(){
            const orderline = super.clone(...arguments);
            orderline.pos_order_line_discounts = this.pos_order_line_discounts;
            return orderline;
        }

        export_as_JSON(){
            var json = super.export_as_JSON();
            var pos_order_line_discounts = [];
            if(this.pos_order_line_discounts){
                this.pos_order_line_discounts.forEach(item => {
                    return pos_order_line_discounts.push([0, 0, item.export_as_JSON()]);
                });
            }
            json.pos_order_line_discounts = pos_order_line_discounts;
            console.log("Export JSON");
            console.log(json.pos_order_line_discounts);
            return json;
        }

        init_from_JSON(json){
            super.init_from_JSON(...arguments);
            console.log("Start Discount Line JSON");                                               
            var line_discounts = json.pos_order_line_discounts;              
            console.log('line_discounts');
            console.log(line_discounts);
            for (var i = 0; i < line_discounts.length; i++) {
                var linediscount = line_discounts[i][2];
                console.log('linediscount ' + i);
                console.log(linediscount);
                var line_discount = DiscountLine.create({}, { orderline: this, json: linediscount });
                console.log('line_discount');
                console.log(line_discount);
                console.log("Start Add Discount Line");
                this.add_line_discount(line_discount);
                console.log(this.pos_order_line_discounts);
                console.log("Finish Add Discount Line");
            }
            console.log("Finish Discount Line");
        }
    }

    Registries.Model.extend(Orderline, DiscountOrderLine);

    const PosOrder = (Order) => 
    class extends Order {	

        apply_member_discount(){

        }
        
        apply_product_discount(product){
            var line = this.get_selected_orderline();
            this.discount = 0;
            console.log('apply_product_discount');
            if(this.pos.get_order().get_aeon_member()){
                console.log("Aeon Member");
                if(this.pos.get_order().get_aeon_member_day()){
                    console.log("Aeon Member Member Day");
                    console.log(product.is_member_day_discount);
                    var is_member_day_discount = product.is_member_day_discount;
                    var is_member_discount = product.is_member_discount;                
                    if(is_member_day_discount){
                        console.log("Aeon Member Day Discount");
                        var categ = product.categ;
                        console.log("categ")
                        console.log(categ);
                        console.log(categ.is_member_day_discount);
                        if (categ.is_member_day_discount){
                            console.log("categ.is_member_day_discount");
                            var linediscount = {
                                discount_source: 'member_day',
                                discount_type: 'percentage',
                                discount_percentage: categ.member_day_discount_percentage,
                                discount_fixed: 0,
                            }
                            var disc_line = DiscountLine.create({}, { orderline: this, json: linediscount });
                            console.log("Add Member Day Discount");
                            console.log(disc_line);
                            line.add_line_discount(disc_line);
                            // this.discount = categ.member_day_discount_percentage;
                        }
                        
                    }
                }
            }
        }
        
		add_product(product, options){
			super.add_product(...arguments);
            this.apply_product_discount(product);
            // var line = this.get_selected_orderline();
            // line.set_discount(line.get_line_total_discounts());
            // this.discount = 0;
		}
        
        export_for_printing() {
            const result = super.export_for_printing(...arguments);
            return result;
        }
	}
	Registries.Model.extend(Order, PosOrder);

    return {        
        DiscountLine,
    };
});
