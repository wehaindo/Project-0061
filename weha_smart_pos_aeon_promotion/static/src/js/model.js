odoo.define('weha_smart_pos_aeon_promotion.models', function (require) {
    "use strict";

    var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
    // var { DiscountLine } = require('weha_smart_pos_aeon_discount.models');
    const Registries = require('point_of_sale.Registries');

    var utils = require('web.utils');
    var round_di = utils.round_decimals;
    var round_pr = utils.round_precision;
    

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
                await this.loadDiscountMultiProducts();
                await this.loadDiscountMultiCategories();
                await this.loadPriceCombinationProducts();
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

            loadPriceCombinationProducts(){
                this.pos_price_combination_products_by_id = {};
                for(const prod of this.pos_price_combination_products){
                    this.pos_price_combination_products_by_id[prod.id] = prod;
                };                
                console.log('loadPriceCombinationProducts');
                console.log(this.pos_price_combination_products);
                console.log(this.pos_price_combination_products_by_id);
            }
        }
    
    Registries.Model.extend(PosGlobalState, PromotionPosGlobalState);

    const PromotionOrderLine = (Orderline) => 
        class extends Orderline {
            constructor(obj, options) {
                super(...arguments);
                this.allowMerge = this.allowMerge || false;
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
            
            // when we add an new orderline we want to merge it with the last line to see reduce the number of items
            // in the orderline. This returns true if it makes sense to merge the two
            can_be_merged_with(orderline){
                console.log('can_be_merged_with');
                var price = parseFloat(round_di(this.price || 0, this.pos.dp['Product Price']).toFixed(this.pos.dp['Product Price']));
                var order_line_price = orderline.get_product().get_price(orderline.order.pricelist, this.get_quantity());
                order_line_price = round_di(orderline.compute_fixed_price(order_line_price), this.pos.currency.decimal_places);
                if( this.get_product().id !== orderline.get_product().id){    //only orderline of the same product can be merged
                    console.log('Diff Product');
                    return false;
                }else if(!this.get_unit() || !this.get_unit().is_pos_groupable){
                    console.log('Diff Unit');
                    return false;
                }else if(this.get_promotion() && !this.get_allow_merge()){
                    return false;                
                // }else if(this.get_discount() > 0 && (!this.get_promotion() && !this.get_allow_merge())){             // we don't merge discounted orderlines
                //     console.log('Have Discount');
                //     return false;                    
                // }else if(!utils.float_is_zero(price - order_line_price - orderline.get_price_extra(),
                //             this.pos.currency.decimal_places)){
                //     console.log('Float is zero');
                //     return false;
                }else if(this.product.tracking == 'lot' && (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots)) {
                    console.log('Diff Lot');
                    return false;
                }else if (this.description !== orderline.description) {
                    console.log('Diff Description');
                    return false;
                }else if (orderline.get_customer_note() !== this.get_customer_note()) {
                    console.log('Diff Note');
                    return false;
                } else if (this.refunded_orderline_id) {
                    console.log('Refund Order Line');
                    return false;
                }else{
                    return true;
                }
            }            
            
            set_allow_merge(allowMerge){
                this.allowMerge = allowMerge
            }

            get_allow_merge(){
                return this.allowMerge;
            }
            
            set_promotion_flag(flag){
                this.promotion_flag = flag;
            }

            get_promotion_flag(){
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
                line.promotion_code = this.promotion ? this.promotion.promotion_code : '';
                line.promotion_description = this.promotion ? this.promotion.promotion_description : '';  
                console.log("export_for_printing");
                console.log(line);              
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
                super.init_from_JSON(...arguments);
                this.uniqueParentId = json.uniqueParentId;
                this.uniqueChildId = json.uniqueChildId;
                this.isRuleApplied = json.isRuleApplied;
                this.promotion = json.promotion;
                this.promotion_flag = json.promotion_flag;
                this.promotion_disc_parentId = json.promotion_disc_parentId;
                this.promotion_disc_childId = json.promotion_disc_childId;
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
                        super.remove_orderline(_line);
                        // return true;
                    }
                }
            }

            remove_orderline(line){
                console.log("Remove Promotion Line");
                console.log(line.get_promotion());
                if (line.get_promotion()){
                    console.log(line.get_promotion());                    
                    this.remove_discount_product(line.get_promotion());                        
                }                
                super.remove_orderline(...arguments);
            }

            check_for_valid_promotion(promotion){
                console.log("Check for valid promotion");                    
                var from_date = new Date(promotion.from_date + ' 00:00:00');
                console.log("from_date");
                console.log(from_date);
                var to_date = new Date(promotion.to_date + ' 23:59:00');                                  
                var current_time = Number(moment(new Date().getTime()).locale('en').format("H"));
                var current_date = Number(moment(new Date().getTime()));
                if (current_date > from_date && current_date < to_date){
                    return true;
                }else{
                    return false;
                }
                // if((Number(promotion.from_time) <= current_time && Number(promotion.to_time) > current_time) || (!promotion.from_time && !promotion.to_time)){                                                               
                //     console.log("Promotion Valid");
                //     return true;
                // } else{
                //     console.log("promotion not Valid");
                //     return false;
                // }
                // return true;
            }

            //Add Product
            add_product(product, options){
                super.add_product(...arguments);
                //create discount percentage
                var line = this.get_selected_orderline();
                // line.set_discount(0);
                // line.set_discount_amount(0);
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
                            // AEON
                            if (promotion.is_member){                            
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_buy_x_get_y_promotion(promotion);
                                }
                            }else{
                                this.apply_buy_x_get_y_promotion(promotion);
                            }
                            break;
                        case 'buy_x_quantity_get_special_price': 
                            // AEON
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
                            //AEON
                            if (promotion.is_member) {
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_fixed_price_on_multi_product(promotion);
                                }
                            }else{
                                this.apply_fixed_price_on_multi_product(promotion);
                            }                                                        
                            break;
                        case 'combination_product_fixed_price': 
                            //AEON
                            if (promotion.is_member) {
                                if(this.pos.get_order().get_aeon_member()){
                                    this.apply_price_combination_products(promotion);
                                }
                            }else{
                                this.apply_price_combination_products(promotion);
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

            // For apply_buy_x_get_y_promotion
            update_promotion_line(orderLine, prom_prod_id, promotion, final_qty){
                var self = this;
                console.log('update_promotion_line');
                let promo_product = this.pos.db.get_product_by_id(prom_prod_id);
                var currentOrderLine = this.get_selected_orderline();    
                if(!orderLine){
                    var new_line = Orderline.create({}, {pos: this.pos, order: this.pos.get_order(), product: promo_product});
                    new_line.set_quantity(final_qty);
                    new_line.price_manually_set = true;
                    new_line.set_unit_price(0);                    
                    new_line.set_unique_child_id(currentOrderLine.get_unique_parent_id());
                    new_line.set_promotion(promotion);
                    new_line.set_price_source('mix_and_match')
                    new_line.set_prc_no(promotion.promotion_code);
                    console.log('this.pos.config.pricelist_id');
                    console.log(this.pos.config.pricelist_id)
                    var default_pricelist = _.find(this.pos.pricelists, function (pricelist) {
                        return pricelist.id === self.pos.config.pricelist_id[0];
                    });                    
                    new_line.set_list_price(promo_product.get_price(default_pricelist, 1))
                    this.pos.get_order().add_orderline(new_line);
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
                    // Looping Check Pos Condition
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

            //BUY X PARTIAL QUANTITY GET SPECIAL PRICE (AEON) 
            async apply_partial_quantity_fixed_price(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;
          
                console.log("check_for_valid_promotion");
                if(promotion.pos_partial_quantity_fixed_price_ids){
                    console.log("pos_partial_quantity_fixed_price_ids");
                    for(const line_id of promotion.pos_partial_quantity_fixed_price_ids){
                        console.log(line_id);
                        var line_promotion = this.pos.pos_partial_quantity_fixed_price_by_id[line_id];
                        console.log("disc_line_record 1");
                        console.log(line_promotion);
                        if(line_promotion){
                            console.log("disc_line_record 2");
                            this.check_partial_products_for_fixed_price(line_promotion, promotion);
                        }
                    }
                } 
            }

            async apply_price_combination_products(promotion){
                var self = this;
                if(!this.check_for_valid_promotion(promotion))
                    return;
                
                var lines = _.filter(self.get_orderlines(), function(line){
                    if(!line.get_promotion()){
                        return line;
                    }
                });
                
                var product_cmp_list = [];
                var orderLine_ids = [];
                var products_qty = [];                
                var promotion_product_ids = [];
                var promotion_products = {};

                for(const promotion_line_id of promotion.combination_product_fixed_price_ids){  
                    // if(promotion_line_id.promotion_id === promotion.id){
                    var promotion_line = this.pos.pos_price_combination_products_by_id[promotion_line_id];                                                                  
                    promotion_product_ids.push(promotion_line.product_id[0]);
                    promotion_products[promotion_line.product_id[0]] = promotion_line.fixed_price;
                    // }                    
                }
                
                console.log("check_for_valid_promotion");      
                const combination_id = Math.floor(Math.random() * 1000000000);          
                if(promotion.combination_product_fixed_price_ids){
                    console.log("combination_product_fixed_price_ids");
                    for(const promotion_line_id of promotion.combination_product_fixed_price_ids){                                                                                            
                        var promotion_line = this.pos.pos_price_combination_products_by_id[promotion_line_id];                        
                        _.each(lines, function(line){                         
                            if(promotion_line.product_id[0] === line.product.id && line.get_quantity() >= promotion_line.quantity_amt ){                                
                                console.log('match');
                                product_cmp_list.push(line.product.id);
                                orderLine_ids.push(line.id);
                                products_qty.push(line.get_quantity());                                
                            }                    
                        });
                    }

                    if(!_.contains(products_qty, 0)){
                        console.log("Product Compare");
                        console.log(product_cmp_list);
                        console.log(promotion_product_ids);
                        console.log(promotion_products);                            
                        if(_.isEqual(_.sortBy(promotion_product_ids), _.sortBy(product_cmp_list))){
                            _.each(orderLine_ids, function(orderLineId){
                                var order_line = self.get_orderline(orderLineId);
                                if(order_line && order_line.get_quantity() > 0){
                                    order_line.price_manually_set = true;
                                    order_line.set_unit_price(promotion_products[order_line.get_product().id]);
                                    order_line.set_promotion(promotion);
                                    order_line.set_combination_id(combination_id);          
                                    order_line.set_price_source('mix_and_match')
                                    order_line.set_prc_no(promotion.promotion_code);
                                    order_line.set_list_price(order_line.product.get_price(self.pos.config.pricelist_id, 1))                                                                                                      
                                    order_line.set_discount_type('fixed');
                                    order_line.set_discount_amount(order_line.get_list_price() - order_line.get_unit_price());
                                }
                            });                 
                        }else{
                            console.log("Product not Equal");    
                        }
                    }
                } 
            }

            //BUY X  QUANTITY GET SPECIAL PRICE (AEON) FOR PARTLY PROMO NO
            async apply_buy_x_get_special_price(promotion){
                if(!this.check_for_valid_promotion(promotion))
                    return;
                
                var match_promotion = this.get_orderlines().find(function(line){
                    return line.get_promotion().id == promotion.id
                });

                // Valid for 1 times promotion
                if(match_promotion){
                    return;
                }

                var selectedOrderLine = this.get_selected_orderline();
                if(selectedOrderLine && promotion.pos_quantity_fixed_price_ids.length > 0){
                    for(const _line_id of promotion.pos_quantity_fixed_price_ids){
                        console.log(_line_id);
                        var _record = this.pos.quantity_fixed_price_by_id[_line_id];
                        console.log(_record);                        
                        if(selectedOrderLine.product.id === _record.product_id[0]){
                            if(selectedOrderLine.quantity >= _record.quantity_amt){
                                const diff_amt = selectedOrderLine.quantity - _record.quantity_amt;                                
                                selectedOrderLine.price_manually_set = true;
                                selectedOrderLine.set_quantity(_record.quantity_amt);
                                selectedOrderLine.set_promotion_flag(true);
                                selectedOrderLine.set_promotion(promotion);
                                selectedOrderLine.set_unit_price(_record.fixed_price);                                        
                                selectedOrderLine.set_price_source('mix_and_match')
                                selectedOrderLine.set_prc_no(promotion.promotion_code);                                
                                selectedOrderLine.set_list_price(selectedOrderLine.product.get_price(this.pos.config.pricelist_id, 1))                                
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
                if(promotion.pos_partial_quantity_fixed_price_ids){
                    console.log("multi_products_fixed_price_ids");
                    for(const line_id of promotion.pos_partial_quantity_fixed_price_ids){
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

            // APPLY FIXED PRICE ON PARTIAL PRODUCTS METHOD - check_products_for_fixed_price
            check_partial_products_for_fixed_price(line_promotion, promotion){                
                var self = this;

                // Check Current Order Lines with same promotion id
                console.log("Get Promotion Lines")
                var promotion_lines = _.filter(self.get_orderlines(), function(line){
                    if(line.get_promotion().id === promotion.id){
                        return line;
                    }
                });

                // Get Order Line with no promotion
                console.log("Get Line without promotion")
                var lines = _.filter(self.get_orderlines(), function(line){
                                if(!line.get_promotion()){
                                    return line;
                                }
                            });
                    
                var product_cmp_list = [];
                var orderLine_ids = [];
                var products_qty = [];
                var total_qty = 0;
                var promotion_qty = 0;
                var diff_qty = 0;


                if(line_promotion.product_ids){                                        
                    if(line_promotion.quantity_amt > 0){
                       _.each(promotion_lines, function(line){
                            if(_.contains(line_promotion.product_ids, line.product.id)){
                                promotion_qty = promotion_qty + line.get_quantity();
                            }
                        });
                    }
                    console.log("promotion_qty");
                    console.log(promotion_qty);        
                    
                    _.each(lines, function(line){
                        if(_.contains(line_promotion.product_ids, line.product.id)){
                            product_cmp_list.push(line.product.id);
                            orderLine_ids.push(line.id);
                            products_qty.push(line.get_quantity());
                            total_qty = total_qty + line.get_quantity();
                        }
                    });         
                    
                    console.log("total_qty");
                    console.log(total_qty);           

                    if(line_promotion.quantity_amt == 0){
                        // if (total_qty >= line_promotion.quantity){
                        if (total_qty >= line_promotion.quantity){
                            if(!_.contains(products_qty, 0)){
                                console.log("total_qty");
                                console.log(total_qty) ;
                                console.log("line_promotion.product_ids");
                                console.log(line_promotion.product_ids);
                                console.log("product_cmp_list");
                                console.log(product_cmp_list);
                                var product_pro_amount = line_promotion.fixed_price / line_promotion.quantity;
                                // let isFound = arr1.some( ai => arr2.includes(ai) );
                                // if(_.isEqual(_.sortBy(line_promotion.product_ids), _.sortBy(product_cmp_list))){
                                if(line_promotion.product_ids.some( ai => product_cmp_list.includes(ai) )){
                                    const combination_id = Math.floor(Math.random() * 1000000000);                                    
                                    _.each(orderLine_ids, function(orderLineId){
                                        var order_line = self.get_orderline(orderLineId);
                                        order_line.set_discount(0);
                                        if(order_line && order_line.get_quantity() > 0){
                                            order_line.price_manually_set = true;
                                            var price = Math.round(product_pro_amount);
                                            // order_line.set_discount(disc_line.products_discount);
                                            // var product_pro_amount = (order_line.quantity / total_qty) * line_promotion.fixed_price;
                                            // var price = 0;
                                            // if(order_line.quantity > 1){
                                            //     price = Math.round(product_pro_amount) / order_line.quantity;
                                            // }else{
                                            //     price = Math.round(product_pro_amount)
                                            // }                                                                                    
                                            // order_line.set_unit_price(line_promotion.fixed_price);                                            
                                            order_line.set_unit_price(price)
                                            order_line.set_promotion(promotion);
                                            order_line.set_price_source('mix_and_match')
                                            order_line.set_prc_no(promotion.promotion_code);
                                            order_line.set_list_price(order_line.product.get_price(self.pos.config.pricelist_id, 1))                                
                                            order_line.set_combination_id(combination_id);                                                                          
                                            order_line.set_discount_type('fixed');                                            
                                            order_line.set_discount_amount(order_line.get_list_price() - price);    
                                            // order_line.set_allow_merge(true);
                                        }
                                    });
                                }
                            }
                        }    
                    }else{
                        if ( total_qty >= line_promotion.quantity && total_qty <= line_promotion.quantity_amt){
                            if(!_.contains(products_qty, 0)){                                
                                if(_.isEqual(_.sortBy(line_promotion.product_ids), _.sortBy(product_cmp_list))){
                                    const combination_id = Math.floor(Math.random() * 1000000000);
                                    _.each(orderLine_ids, function(orderLineId){
                                        var order_line = self.get_orderline(orderLineId);
                                        order_line.set_discount(0);
                                        if(order_line && order_line.get_quantity() > 0){
                                            order_line.price_manually_set = true;                                                                                                                                                                                
                                            order_line.set_unit_price(line_promotion.fixed_price);
                                            order_line.set_promotion(promotion);
                                            order_line.set_price_source('mix_and_match')
                                            order_line.set_prc_no(promotion.promotion_code);
                                            order_line.set_list_price(order_line.product.get_price(self.pos.config.pricelist_id, 1))                                
                                            order_line.set_combination_id(combination_id);
                                            order_line.set_allow_merge(true);
                                        }
                                    });
                                }
                            }                               
                        }
                        if(promotion_qty === line_promotion.quantity_amt){
                            _.each(promotion_lines, function(line){
                                line.set_allow_merge(false);
                            });   
                        }
                    }                    
                }
            }

            check_price_combination_products(line_promotion, promotion){
                var self = this;
                var lines = _.filter(self.get_orderlines(), function(line){
                                if(!line.get_promotion()){
                                    return line;
                                }
                            });
                var product_cmp_list = [];
                var orderLine_ids = [];
                var products_qty = [];                
                if(line_promotion.product_id){
                    _.each(lines, function(line){
                        if(line_promotion.product_id.id === line.product_id.id){
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
                                    order_line.set_discount_type('fixed');
                                    order_line.set_discount_amount(order_line.get_list_price() - disc_line.fixed_price);    
                                }
                            });
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