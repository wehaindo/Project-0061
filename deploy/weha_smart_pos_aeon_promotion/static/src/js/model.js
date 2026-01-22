odoo.define('weha_smart_pos_aeon_promotion.models', function (require) {
    "use strict";

    var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
    var { DiscountLine } = require('weha_smart_pos_aeon_discount.models');
    const Registries = require('point_of_sale.Registries');


    const PromotionPosGlobalState = (PosGlobalState) => 
        class  extends PosGlobalState {
            constructor(obj) {
                super(obj);
            }

            async _processData(loadedData) {
                await super._processData(...arguments);
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
                await this.loadPosPromotion();                
                await this.loadPosCondition();
                await this.loadPartialQuantityFixedPrice();
                await this.loadQuantityFixedPrice();
                await this.loadGetDiscount();
                await this.loadQuantityDiscount();
                await this.loadQuantityDiscountAmt();
                await this.loadFixedPriceMultiProducts();
                await this.loadFreeProductMultiProducts();
                await this.loadDiscountMultiProducts();
                await this.loadDiscountMultiCategories();
            }
            
            loadPosPromotion(){
                this.pos_promotions_by_id = {};
                for(const pos_promotions of this.pos_promotions){
                    this.pos_promotions_by_id[pos_promotions.id] = pos_promotions;
                };
            }

            loadPosCondition(){
                this.pos_conditions_by_id = {};
                for(const pos_condition of this.pos_conditions){
                    this.pos_conditions_by_id[pos_condition.id] = pos_condition;
                };
            }

            loadPartialQuantityFixedPrice(){
                this.pos_partial_quantity_fixed_price_by_id = {};
                for(const pos_partial_quantity_fixed_price of this.pos_partial_quantity_fixed_prices){
                    this.pos_partial_quantity_fixed_price_by_id[pos_partial_quantity_fixed_price.id] = pos_partial_quantity_fixed_price;
                };
            }

            loadQuantityFixedPrice(){
                this.quantity_fixed_price_by_id = {};
                for(const quantity_fixed_price of this.quantity_fixed_prices){
                    this.quantity_fixed_price_by_id[quantity_fixed_price.id] = quantity_fixed_price;
                };
            }

            loadGetDiscount(){
                this.get_discount_by_id = {};
                for(const get_discount of this.get_discount){
                    this.get_discount_by_id[get_discount.id] = get_discount;
                };
            }

            loadQuantityDiscount(){
                this.quantity_discount_by_id = {};
                for(const pos_get_qty_discount of this.pos_get_qty_discount){
                    this.get_discount_by_id[pos_get_qty_discount.id] = pos_get_qty_discount;
                };
            }

            loadQuantityDiscountAmt(){
                this.quantity_discount_amt_by_id = {};
                for(const pos_get_qty_discount_amt of this.pos_get_qty_discount_amt){
                    this.get_discount_amt_by_id[pos_get_qty_discount_amt.id] = pos_get_qty_discount_amt;
                };
            }

            loadFixedPriceMultiProducts(){
                this.pos_fixed_price_multi_prods_by_id = {};
                for(const prod of this.pos_fixed_price_multi_prods){
                    this.pos_fixed_price_multi_prods_by_id[prod.id] = prod;
                };
            }

            loadFreeProductMultiProducts(){
                this.pos_free_product_multi_prods_by_id = {};
                for(const prod of this.pos_free_product_multi_prods){
                    this.pos_free_product_multi_prods_by_id[prod.id] = prod;
                };
            }

            loadDiscountMultiProducts(){
                this.pos_discount_multi_prods_by_id = {};
                for(const prod of this.pos_discount_multi_prods){
                    this.pos_discount_multi_prods_by_id[prod.id] = prod;
                };
            }

            loadDiscountMultiCategories(){
                this.pos_discount_multi_category_by_id = {};
                for(const pos_discount_multi_category of this.pos_discount_multi_category){
                    this.pos_discount_multi_category_by_id[pos_discount_multi_category.id] = pos_discount_multi_category;
                };
            }

            loadDiscountAbovePrice(){
                this.pos_discount_above_price = pos_discount_above_price;
            }
        }
    
    Registries.Model.extend(PosGlobalState, PromotionPosGlobalState);

    const PromotionOrderLine = (Orderline) => 
        class extends Orderline {
            constructor(obj, options) {
                super(...arguments);
                this.uniqueChildId = this.uniqueChildId || false;
                this.uniqueParentId = this.uniqueParentId || false;
                this.isRuleApplied = this.isRuleApplied || false;
                this.promotionRule = this.promotionRule || false;
                this.promotion = this.promotion || false;
                this.combination_id = this.combination_id || false;
                this.parent_combination_id = this.parent_combination_id || false;
                this.promotion_flag = this.promotion_flag || false;
                this.promotion_disc_parentId = this.promotion_disc_parentId || false;
                this.promotion_disc_childId = this.promotion_disc_childId || false;
            }
            
            // setup(){
            //     super.setup();
            //     this.uniqueChildId = this.uniqueChildId || false;
            //     this.uniqueParentId = this.uniqueParentId || false;
            //     this.isRuleApplied = this.isRuleApplied || false;
            //     this.promotionRule = this.promotionRule || false;
            //     this.promotion = this.promotion || false;
            //     this.combination_id = this.combination_id || false;
            //     this.promotion_flag = this.promotion_flag || false;
            //     this.promotion_disc_parentId = this.promotion_disc_parentId || false;
            //     this.promotion_disc_childId = this.promotion_disc_childId || false;
            // }
            
            set_promotion_flag(flag){
                this.promotion_flag = flag;
            }

            get_promotion_flag(flag){
                return this.promotion_flag;
            }

            set_promotion_disc_parent_id(parentId){
                this.promotion_disc_parentId = parentId;
            }

            get_promotion_disc_parent_id(){
                return this.promotion_disc_parentId;
            }

            set_promotion_disc_child_id(childId){
                this.promotion_disc_childId = childId;
            }

            get_promotion_disc_child_id(){
                return this.promotion_disc_childId;
            }

            set_combination_id(combinationId){
                this.combination_id = combinationId;
            }

            get_combination_id(){
                return this.combination_id;
            }

            set_parent_combination_id(combinationId){
                this.parent_combination_id = combinationId;
            }

            get_parent_combination_id(){
                return this.parent_combination_id;
            }

            //FOR BUY X GET Y FREE PRODUCT START
            set_unique_parent_id(uniqueParentId){
                this.uniqueParentId = uniqueParentId;
            }

            get_unique_parent_id(){
                return this.uniqueParentId;
            }

            set_unique_child_id(uniqueChildId){
                this.uniqueChildId = uniqueChildId;
            }

            get_unique_child_id(){
                return this.uniqueChildId;
            }

            //FOR BUY X GET Y FREE PRODUCT END
            set_promotion(promotion){
                this.promotion = promotion;
            }
            
            get_promotion(promotion){
                return this.promotion;
            }

            set_is_rule_applied(rule){
                this.applied_rule = rule;
            }

            get_is_rule_applied (){
                return this.applied_rule;
            }

            set_is_promotion_applied(rule){
                this.is_promotion_applied = rule;
            }

            get_is_promotion_applied(){
                return this.is_promotion_applied;
            }

            set_buy_x_get_dis_y(product_ids){
                this.product_ids = product_ids;
            }

            get_buy_x_get_dis_y(){
                return this.product_ids;
            }

            clone(){
                var orderLine = super.clone();
                orderLine.uniqueParentId = this.uniqueParentId;
                orderLine.uniqueChildId = this.uniqueChildId;
                orderLine.isRuleApplied = this.isRuleApplied;
                orderLine.promotion = this.promotion;
                orderLine.combination_id = this.combination_id;
                orderLine.parent_combination_id = this.parent_combination_id;
                orderLine.promotion_flag = this.promotion_flag;
                orderLine.promotion_disc_parentId = this.promotion_disc_parentId;
                orderLine.promotion_disc_childId = this.promotion_disc_childId;
                return orderLine;
            }

            export_for_printing() {
                var line = super.export_for_printing(...arguments);
                line.promotion_code = this.promotion ? this.promotion.promotion_code : false;
                return line;
            }

            export_as_JSON(){
                var json = super.export_as_JSON();
                json.uniqueParentId = this.uniqueParentId;
                json.uniqueChildId = this.uniqueChildId;
                json.isRuleApplied = this.isRuleApplied;
                json.promotion = this.promotion;
                json.combination_id = this.combination_id;
                json.parent_combination_id = this.parent_combination_id;
                json.promotion_flag = this.promotion_flag;
                json.promotion_disc_parentId = this.promotion_disc_parentId;
                json.promotion_disc_childId = this.promotion_disc_childId;
                return json;
            }
            
            init_from_JSON(json){
                this.uniqueParentId = json.uniqueParentId;
                this.uniqueChildId = json.uniqueChildId;
                this.isRuleApplied = json.isRuleApplied;
                this.promotion = json.promotion;
                this.promotion_flag = json.promotion_flag;
                this.promotion_disc_parentId = json.promotion_disc_parentId;
                this.promotion_disc_childId = json.promotion_disc_childId;
                super.init_from_JSON(...arguments);
            }


        }
    
    Registries.Model.extend(Orderline, PromotionOrderLine);

    const PromotionOrder = (Order) => 
        class extends Order {
            constructor(obj, options) {
                super(...arguments);
                this.orderPromotion = this.orderPromotion || false;
                this.orderDiscountLine = this.orderDiscountLine || false;
            }

            // setup() {
            //     super.setup();
            //     this.orderPromotion = this.orderPromotion || false;
            //     this.orderDiscountLine = this.orderDiscountLine || false;
            // }

            init_from_JSON(json) {
                super.init_from_JSON(...arguments);
                this.orderPromotion = json.orderPromotion;
                this.orderDiscountLine = json.orderDiscountLine;
            }
            
            export_as_JSON() {
                const json = super.export_as_JSON(...arguments);
                json.orderPromotion = this.orderPromotion || false;
                json.orderDiscountLine = this.orderDiscountLine || false;
                return json;
            }

            set_order_total_discount_line(line){
                this.orderDiscountLine = line;
            }

            get_order_total_discount_line(){
                return this.orderDiscountLine;
            }

            get_orderline_by_unique_id(uniqueId){
                var orderlines = this.orderlines;
                for(var i = 0; i < orderlines.length; i++){
                    if(orderlines[i].uniqueChildId === uniqueId){
                        return orderlines[i];
                    }
                }
                return null;
            }

            set_order_total_discount(promotion){
                this.orderPromotion = promotion;
            }

            async apply_pos_order_discount_total(){
                var filteredPromotion = _.filter(this.pos.pos_promotions, function(promotion){
                                            return promotion.promotion_type == 'discount_total'
                                        })
                var total = this.get_total_with_tax();
                for(const promotion of filteredPromotion){
                    console.log(promotion);
                    if(!this.check_for_valid_promotion(promotion))
                        return;
                    var discountProduct = this.pos.db.get_product_by_id(promotion.discount_product[0]);
                    if(total >= promotion.total_amount){
                        var isDiscount = await this.remove_discount_product(promotion)
                        var createNewDiscountLine = Orderline.create({}, {pos: this.pos,order: this.pos.get_order(), product: discountProduct});
                        console.log("createNewDiscountLine");
                        console.log(createNewDiscountLine);
                        const discount = - (total * promotion.total_discount)/100;
                        createNewDiscountLine.set_quantity(1);
                        createNewDiscountLine.price_manually_set = true;
                        createNewDiscountLine.set_unit_price(discount);
                        createNewDiscountLine.set_promotion(promotion);
                        //this.orderlines.add(createNewDiscountLine);
                        this.add_orderline(createNewDiscountLine);
                        this.set_order_total_discount(promotion);
                        //this.set_order_total_discount_line(createNewDiscountLine);
                    }
                }
            }

            remove_discount_product(promotion){
                for(const _line of this.get_orderlines()){
                    if(_line.product.id === promotion.discount_product[0]){
                        this.remove_orderline(_line);
                        return true;
                    }
                }
            }


            // remove_orderline(line){c
            //     console.log("Remove Promotion Line");
            //     console.log(line.get_promotion());
            //     this.remove_discount_product(line.get_promotion());
            //     super.remove_orderline(...arguments);
            // }



            check_for_valid_promotion(promotion){
                console.log("Check for valid promotion");
                var current_time = Number(moment(new Date().getTime()).locale('en').format("H"));
                if((Number(promotion.from_time) <= current_time && Number(promotion.to_time) > current_time) || (!promotion.from_time && !promotion.to_time)){
                    console.log("Promotion Valid");
                    return true;
                } else{
                    console.log("promotion not Valid");
                    return false;
                }
            }

            //Add Product
            add_product(product, options){
                super.add_product(...arguments);
                console.log("Check Promotion");
                this.apply_pos_promotion(product);
                this.apply_pos_order_discount_total();
            }

            apply_pos_promotion(product){
                var current_time = Number(moment(new Date().getTime()).locale('en').format("H"));
                var selectedLine =  this.get_selected_orderline();
    
                for(var promotion of this.pos.pos_promotions){
                    let promotion_type = promotion.promotion_type;
                    let flag = false;
                    switch (promotion_type) {
                        case 'buy_x_get_y':
                            if (promotion.is_member){                            
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_buy_x_get_y_promotion(promotion);
                                }
                            }else{
                                this.apply_buy_x_get_y_promotion(promotion);
                            }
                            break;
                        case 'buy_x_quantity_get_special_price':
                            if (promotion.is_member){                            
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_buy_x_get_special_price(promotion);
                                }
                            }else{
                                this.apply_buy_x_get_special_price(promotion);
                            }
                        case 'buy_x_partial_quantity_get_special_price':
                            if (promotion.is_member){                            
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_partial_quantity_fixed_price(promotion);
                                }
                            }else{
                                this.apply_partial_quantity_fixed_price(promotion);
                            }
                        case 'buy_x_get_dis_y':
                            console.log(promotion.promotion_code);
                            console.log(promotion.is_member);
                            console.log(this.pos.get_order().get_aeon_member());
                            if (promotion.is_member) {
                                console.log('Pass Is Member');
                                if(this.pos.get_order().get_aeon_member()){
                                    console.log('Pass Member Exist');
                                    this.apply_buy_x_disc_y_promotion(promotion);
                                }
                            }else{
                                this.apply_buy_x_disc_y_promotion(promotion);
                            }
                            break;
                        case 'quantity_discount':
                            if (promotion.is_member) {
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_quantity_discount(promotion);
                                }
                            }else{
                                this.apply_quantity_discount(promotion);
                            }
                            break;
                        case 'quantity_price':
                            if (promotion.is_member) {
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_quantity_price(promotion);
                                }
                            }else{
                                this.apply_quantity_price(promotion);
                            }
                            break;
                        case 'fixed_price_on_multi_product': 
                            if (promotion.is_member) {
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_fixed_price_on_multi_product(promotion);
                                }
                            }else{
                                this.apply_fixed_price_on_multi_product(promotion);
                            }                                                        
                            break;                            
                        case 'free_product_on_multi_product': 
                            if (promotion.is_member) {
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_free_product_on_multi_product(promotion);
                                }
                            }else{
                                this.apply_free_product_on_multi_product(promotion);
                            }                                                        
                            break;                                                        
                        case 'discount_on_multi_product':
                            if (promotion.is_member) {
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_discount_on_multi_product(promotion);
                                }
                            }else{
                                this.apply_discount_on_multi_product(promotion);
                            }                                                        
                            break;
                        case 'discount_on_multi_category':
                            if (promotion.is_member) {
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_discount_on_multi_category(promotion, product);
                                }
                            }else{
                                this.apply_discount_on_multi_category(promotion, product);
                            }                            
                            break;
                    }
                }
            }

            update_promotion_line(orderLine, prom_prod_id, promotion, final_qty){
                let promo_product = this.pos.db.get_product_by_id(prom_prod_id);
                var currentOrderLine = this.get_selected_orderline();
    
                if(!orderLine){
                    var new_line = Orderline.create({}, {pos: this.pos, order: this.pos.get_order(), product: promo_product});
                        new_line.set_quantity(final_qty);
                        new_line.price_manually_set = true;
                        new_line.set_unit_price(0);
                        // new_line.set_unit_price(this.promo_product.get_price(this.pos.get_order().pricelist, this.get_quantity()))
                        new_line.set_unique_child_id(currentOrderLine.get_unique_parent_id());
                        new_line.set_promotion(promotion);
                        var linediscount = {
                            discount_type: 'fixed',
                            discount_percentage: 10,
                            discount_fixed: new_line.get_price_with_tax(),
                        }
                        // var line_discount = DiscountLine.create({}, { orderline: new_line, json: linediscount });
                        // new_line.add_line_discount(line_discount);
                        // console.log("new_line.get_line_total_discounts()");
                        // console.log(new_line);
                        // console.log(new_line.get_line_total_discounts());
                        // new_line.set_discount(new_line.get_line_total_discounts());
                        this.pos.get_order().add_orderline(new_line);
                        // currentOrderLine = this.get_selected_orderline();
                        // currentOrderLine.set_discount(currentOrderLine.get_line_total_discounts());
                        
                }else{
                    orderLine.price_manually_set = true;
                    orderLine.set_unit_price(0);
                    orderLine.set_quantity(final_qty);
                }
                this.select_orderline(currentOrderLine);
            }

            async apply_buy_x_get_y_promotion(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;
                var selectedOrderLine = this.get_selected_orderline();
                if(selectedOrderLine && promotion.pos_condition_ids.length > 0){
                    for(const _line_id of promotion.pos_condition_ids){
                        var _record = this.pos.pos_conditions_by_id[_line_id];
                        if(selectedOrderLine.product.id === _record.product_x_id[0]){
                            // let prom_qty = Math.floor(selectedOrderLine.quantity / _record.quantity);
                            // let final_qty = Math.floor(prom_qty * _record.quantity_y);
                            // if(_record.operator === 'greater_than_or_eql' && selectedOrderLine.quantity >= _record.quantity){
                            if(selectedOrderLine.quantity >= _record.quantity){
                                if(selectedOrderLine && !selectedOrderLine.get_unique_parent_id()){
                                    selectedOrderLine.set_unique_parent_id(Math.floor(Math.random() * 1000000000));
                                    var parentId = await selectedOrderLine ? selectedOrderLine.get_unique_parent_id() : false;
                                    var childOrderLine = this.get_orderline_by_unique_id(parentId ? selectedOrderLine.get_unique_parent_id() : false);
                                    this.update_promotion_line(childOrderLine, _record.product_y_id[0], promotion, _record.quantity_y);    
                                }
                            }
                            break;
                        }
                    }
                }
            }            
            
            //BUY X GET Y FREE PROMOTION END
            apply_buy_x_disc_y_promotion(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;

                var SelectedLine = this.get_selected_orderline();
                var _lineById = [];
                var orderLines = _.filter(this.get_orderlines(), function(line){
                                     if(!line.get_promotion()){
                                         return line;
                                     }
                                 });
                var lineProductIds = _.pluck(_.pluck(orderLines, 'product'),  'id');
                var flag = false;
                var discountLineList = [];
                if(promotion && !promotion.parent_product_ids){
                    return false;
                };
                for(var _line of orderLines){
                    if(_.contains(promotion && promotion.parent_product_ids, _line.product.id)){
                        if(!_line.get_promotion_flag() && !_line.get_unique_parent_id()){
                            _lineById.push(_line);
                        }
                        for(const discId of promotion.pos_quantity_dis_ids){
                            let discountLineRecord = this.pos.get_discount_by_id[discId];
                                discountLineRecord && discountLineRecord.product_id_dis ? discountLineList.push(discountLineRecord) : '';
                        }
                        flag = true;
                        break;
                    }
                }
                if(!flag){
                    return;
                }
                for(var _line of orderLines){
                    for(const _discount of discountLineList){
                        if(_discount.product_id_dis && _discount.product_id_dis[0] == _line.product.id){
                            var parentLine =  _.filter(_lineById, function(line){
                                         if(!line.get_promotion_disc_parent_id() && _.contains(promotion.parent_product_ids, line.product.id)){
                                             return line;
                                         }
                                     });
                            if(parentLine.length > 0 && _line.quantity >= _discount.qty){
                                if(parentLine.length > 0 && !parentLine[0].get_promotion_disc_parent_id()){
                                    parentLine[0].set_promotion_disc_parent_id(Math.floor(Math.random() * 1000000000));
                                    parentLine[0].set_unique_parent_id(null);
                                    parentLine[0].set_promotion_flag(true);
                                }
                                _line.set_promotion(promotion);
                                _line.set_discount(_discount.discount_dis_x);
                                _line.set_promotion_disc_child_id(parentLine[0].get_promotion_disc_parent_id());
                            }
                        }
                    }
                }
            }

            async apply_partial_quantity_fixed_price(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;
        
                var match_promotion = this.get_orderlines().find(function(line){
                    return line.get_promotion().id == promotion.id
                });

                var match_promotion_lines = _.filter(this.get_orderlines(), function(line){
                    if(line.get_promotion() && line.get_promotion().id == promotion.id){
                        return line;
                    }
                });
                
            

 
                // if(match_promotion){
                //     return;
                // }

                var selectedOrderLine = this.get_selected_orderline();
                if(selectedOrderLine && promotion.pos_partial_quantity_fixed_price_ids.length > 0){
                    console.log('apply_partial_quantity_fixed_price level 1')
                    for(const _line_id of promotion.pos_partial_quantity_fixed_price_ids){
                        console.log('apply_partial_quantity_fixed_price level 2')
                        console.log(_line_id);
                        var _record = this.pos.pos_partial_quantity_fixed_price_by_id[_line_id];
                        console.log(_record);                                                
                        if(selectedOrderLine.product.id === _record.product_id[0]){
                            if(_record.quantity_amt == 0){
                                console.log('apply_partial_quantity_fixed_price level 3')
                                if(match_promotion_lines && match_promotion_lines.length > 0){                                                                    
                                    var match_promotion_line = match_promotion_lines[0];
                                    match_promotion_line.price_manually_set = true;                                    
                                    match_promotion_line.set_unit_price(_record.fixed_price);            
                                    match_promotion_line.set_promotion_flag(true);
                                    match_promotion_line.set_promotion(promotion);                                        
                                    match_promotion_line.set_quantity(match_promotion_line.get_quantity() + selectedOrderLine.get_quantity())                                                                    
                                    // match_promotion_line.set_selected(true);
                                    // this.get_orderlines().remove(selectedOrderLine);
                                }else{
                                    // New Line for Promotion Product
                                    if(selectedOrderLine.quantity <= _record.quantity){                                    
                                        selectedOrderLine.price_manually_set = false;                                    
                                        selectedOrderLine.set_unit_price(_record.fixed_price);            
                                        selectedOrderLine.set_promotion_flag(true);
                                        selectedOrderLine.set_promotion(promotion);                                        
                                    }    
                                }       
                            }                            
                            break;
                        }
                    }
                }
 
            }

            async apply_buy_x_get_special_price(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;
                
                var match_promotion = this.get_orderlines().find(function(line){
                    return line.get_promotion().id == promotion.id
                });

                if(match_promotion){
                    return;
                }

                var selectedOrderLine = this.get_selected_orderline();
                if(selectedOrderLine && promotion.pos_quantity_fixed_price_ids.length > 0){
                    console.log('apply_buy_x_get_special_price level 1')
                    for(const _line_id of promotion.pos_quantity_fixed_price_ids){
                        console.log('apply_buy_x_get_special_price level 2')
                        console.log(_line_id);
                        var _record = this.pos.quantity_fixed_price_by_id[_line_id];
                        console.log(_record);                        
                        if(selectedOrderLine.product.id === _record.product_id[0]){
                            console.log('apply_buy_x_get_special_price level 3')
                            if(selectedOrderLine.quantity >= _record.quantity_amt){
                                console.log('apply_buy_x_get_special_price level 4')
                                const diff_amt = selectedOrderLine.quantity - _record.quantity_amt;
                                selectedOrderLine.price_manually_set = true;
                                selectedOrderLine.set_quantity(_record.quantity_amt);
                                selectedOrderLine.set_promotion_flag(true);
                                selectedOrderLine.set_promotion(promotion);
                                selectedOrderLine.set_unit_price(_record.fixed_price);        
                                if (diff_amt > 0){
                                    var createNewOrderLine = Orderline.create({}, {pos: this.pos,order: this.pos.get_order(), product: selectedOrderLine.product});                            
                                    console.log("diff_amt");
                                    console.log(diff_amt);
                                    createNewOrderLine.set_quantity(diff_amt);
                                    this.orderlines.add(createNewOrderLine);
                                }                                            
                            }
                            break;
                        }
                    }
                }
            }

            //APPLY PERCENTAGE DISCOUNT ON QUANTITY DONE
            apply_quantity_discount(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;
                var selected_line = this.get_selected_orderline();
                const {product_id_qty} = promotion;
                if(selected_line && product_id_qty && product_id_qty[0] === selected_line.product.id){
                    for(const promo_id of promotion.pos_quantity_ids){
                        var line_record = this.pos.get_qty_discount_by_id[promo_id];
                        if(line_record && selected_line.quantity >= line_record.quantity_dis){
                            if(line_record.discount_dis){
                                selected_line.set_promotion(promotion);
                                selected_line.set_discount(line_record.discount_dis);
                            }
                        }
                    }
                }
            }
            
            //APPLY PERCENTAGE DISCOUNT ON QUANTITY END
            apply_quantity_price(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;
                var selected_line = this.get_selected_orderline();
                if(selected_line && promotion.product_id_amt && promotion.product_id_amt[0] == selected_line.product.id){
                    for(const qty_amt_id of promotion.pos_quantity_amt_ids){
                        let line_record = this.pos.pos_qty_discount_amt_by_id[qty_amt_id];
                        if(line_record && selected_line.quantity >= line_record.quantity_amt){
                            if(line_record.discount_price){
                                selected_line.set_promotion(promotion);
                                selected_line.set_unit_price(((selected_line.get_unit_price() * selected_line.get_quantity()) -
                                line_record.discount_price)/selected_line.get_quantity());
                                break;
                            }
                        }
                    }
                }
            }

            // APPLY FIXED PRICE ON MULTIPLE PRODUCTS
            apply_fixed_price_on_multi_product(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;
          
                console.log("check_for_valid_promotion");
                if(promotion.multi_products_fixed_price_ids){
                    console.log("multi_products_fixed_price_ids");
                    for(const line_id of promotion.multi_products_fixed_price_ids){
                        console.log(line_id);
                        var line_record = this.pos.pos_fixed_price_multi_prods_by_id[line_id];
                        console.log("disc_line_record 1");
                        console.log(line_record);
                        if(line_record){
                            console.log("disc_line_record 2");
                            this.check_products_for_fixed_price(line_record, promotion);
                        }
                    }
                }
            }
            
            // APPLY FREE PRODUCT ON MULTIPLE PRODUCTS
            apply_free_product_on_multi_product(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;
          
                console.log("check_for_valid_promotion");
                if(promotion.multi_products_free_product_ids){
                    console.log("multi_products_free_product_ids");
                    for(const line_id of promotion.multi_products_free_product_ids){
                        console.log(line_id);
                        var line_record = this.pos.pos_free_product_multi_prods_by_id[line_id];
                        console.log("disc_line_record 1");
                        console.log(line_record);
                        if(line_record){
                            console.log("disc_line_record 2");
                            this.check_products_for_free_product(line_record, promotion);
                        }
                    }
                }
            }

            // APPLY DISCOUNT ON MULTIPLE PRODUCTS
            apply_discount_on_multi_product(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;
          
                console.log("check_for_valid_promotion");
                if(promotion.multi_products_discount_ids){
                    console.log("multi_products_discount_ids");
                    for(const disc_line_id of promotion.multi_products_discount_ids){
                        console.log(disc_line_id);
                        var disc_line_record = this.pos.pos_discount_multi_prods_by_id[disc_line_id];
                        console.log("disc_line_record 1");
                        console.log(this.pos.pos_discount_multi_prods_by_id)
                        console.log(disc_line_record);
                        if(disc_line_record){
                            console.log("disc_line_record 2");
                            this.check_products_for_disc(disc_line_record, promotion);
                        }
                    }
                }
            }

            // APPLY FIXED PRICE ON MULTIPLE PRODUCTS METHOD - check_products_for_fixed_price
            check_products_for_fixed_price(disc_line, promotion){
                var self = this;
                var lines = _.filter(self.get_orderlines(), function(line){
                                if(!line.get_promotion()){
                                    return line;
                                }
                            });
                var product_cmp_list = [];
                var orderLine_ids = [];
                var products_qty = [];
                if(disc_line.product_ids && disc_line.products_discount){
                    _.each(lines, function(line){
                        if(_.contains(disc_line.product_ids, line.product.id)){
                            product_cmp_list.push(line.product.id);
                            orderLine_ids.push(line.id);
                            products_qty.push(line.get_quantity());
                        }
                    });
                    if(!_.contains(products_qty, 0)){
                        if(_.isEqual(_.sortBy(disc_line.product_ids), _.sortBy(product_cmp_list))){
                            const combination_id = Math.floor(Math.random() * 1000000000);
                            _.each(orderLine_ids, function(orderLineId){
                                var order_line = self.get_orderline(orderLineId);
                                if(order_line && order_line.get_quantity() > 0){
                                    order_line.price_manually_set = true;
                                    // order_line.set_discount(disc_line.products_discount);
                                    order_line.set_unit_price(disc_line.fixed_price);
                                    order_line.set_promotion(promotion);
                                    order_line.set_combination_id(combination_id);
                                }
                            });
                        }
                    }
                }

            }

            // APPLY FREE PRODUCT ON MULTIPLE PRODUCTS METHOD - check_products_for_free_product
            check_products_for_free_product(disc_line, promotion){
                var self = this;
                var lines = _.filter(self.get_orderlines(), function(line){
                                if(!line.get_promotion()){
                                    return line;
                                }
                            });
                var product_cmp_list = [];
                var orderLine_ids = [];
                var products_qty = [];
                if(disc_line.product_ids && disc_line.product_id){
                    _.each(lines, function(line){
                        if(_.contains(disc_line.product_ids, line.product.id)){
                            product_cmp_list.push(line.product.id);
                            orderLine_ids.push(line.id);
                            products_qty.push(line.get_quantity());
                        }
                    });
                    if(!_.contains(products_qty, 0)){
                        if(_.isEqual(_.sortBy(disc_line.product_ids), _.sortBy(product_cmp_list))){
                            const combination_id = Math.floor(Math.random() * 1000000000);
                            _.each(orderLine_ids, function(orderLineId){
                                var order_line = self.get_orderline(orderLineId);
                                if(order_line && order_line.get_quantity() > 0){
                                    order_line.set_promotion(promotion);
                                    order_line.set_combination_id(combination_id);
                                }
                            });
                            //Add Free Product Order Line
                            console.log("disc_line.product_id");
                            console.log(disc_line.product_id);
                            var free_product = self.pos.db.get_product_by_id(disc_line.product_id[0]);
                            console.log("free_product");
                            console.log(free_product);
                            var createNewOrderLine = Orderline.create({}, {pos: self.pos,order: self.pos.get_order(), product: free_product});                            
                            console.log("quantity_amt");
                            console.log(disc_line.quantity_amt);                            
                            createNewOrderLine.price_manually_set = true;
                            createNewOrderLine.set_unit_price(0);
                            createNewOrderLine.set_quantity(disc_line.quantity_amt);
                            createNewOrderLine.set_promotion(promotion);
                            this.add_orderline(createNewOrderLine);
                        }
                    }
                }
            }

            // APPLY DISCOUNT ON MULTIPLE PRODUCTS METHOD - check_products_for_disc
            check_products_for_disc(disc_line, promotion){
                var self = this;
                var lines = _.filter(self.get_orderlines(), function(line){
                                if(!line.get_promotion()){
                                    return line;
                                }
                            });
                var product_cmp_list = [];
                var orderLine_ids = [];
                var products_qty = [];
                if(disc_line.product_ids && disc_line.products_discount){
                    _.each(lines, function(line){
                        if(_.contains(disc_line.product_ids, line.product.id)){
                            product_cmp_list.push(line.product.id);
                            orderLine_ids.push(line.id);
                            products_qty.push(line.get_quantity());
                        }
                    });
                    if(!_.contains(products_qty, 0)){
                        if(_.isEqual(_.sortBy(disc_line.product_ids), _.sortBy(product_cmp_list))){
                            const combination_id = Math.floor(Math.random() * 1000000000);
                            _.each(orderLine_ids, function(orderLineId){
                                var order_line = self.get_orderline(orderLineId);
                                if(order_line && order_line.get_quantity() > 0){
                                    order_line.set_discount(disc_line.products_discount);
                                    order_line.set_promotion(promotion);
                                    order_line.set_combination_id(combination_id);
                                }
                            });
                        }
                    }
                }
            }

            // APPLY DISCOUNT ON MULTIPLE CATEGORIES DONE
            apply_discount_on_multi_category(promotion, product){
                if(!this.check_for_valid_promotion(promotion))
                    return;
                var selected_line = this.get_selected_orderline();
                if(!product) return;
                if(promotion.multi_category_discount_ids){
                    for(const disc_id of promotion.multi_category_discount_ids){
                        let disc_obj = this.pos.pos_discount_multi_category_by_id[disc_id];
                        if(disc_obj && disc_obj.category_ids && disc_obj.category_discount, product.pos_categ_id[0]){
                            if(_.contains(disc_obj.category_ids ,  product.pos_categ_id[0])){
                                selected_line.set_discount(disc_obj.category_discount);
                                selected_line.set_promotion(promotion);
                                break;
                            }
                        }
                    }
                };
            }
        }

    Registries.Model.extend(Order, PromotionOrder);


});