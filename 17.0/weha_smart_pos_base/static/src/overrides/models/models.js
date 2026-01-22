/** @odoo-module */

import { register_payment_method } from "@point_of_sale/app/store/pos_store";
import { PaymentDeposit } from "@weha_smart_pos_base/app/pos_deposit/payment_deposit";
import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

const { DateTime } = luxon;

patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);        
        this.is_deposit_order = this.is_deposit_order || false;  
        this.orderPromotion = this.orderPromotion || false;
        this.orderDiscountLine = this.orderDiscountLine || false;
    },
    can_be_merged_with(orderline){
        if(orderline.get_promotion() && !orderline.get_allow_merge()){
            return false;         
        }else{     
            return super.can_be_merged_with(...arguments);
        }
    },
    set_is_deposit_order(is_deposit_order){
        this.is_deposit_order = is_deposit_order
    },
    get_is_deposit_order(){
        return this.is_deposit_order;
    },
    add_product(product, options){
        if(this.get_is_deposit_order()){
            return
        }
        super.add_product(product,options);
        this.apply_pos_promotion(product);        
    },
    remove_orderline(line){        
        super.remove_orderline(line);
        if(this.orderlines.length == 0 && this.get_is_deposit_order()){
            this.set_is_deposit_order(false);
        }        
    },
    async remove_paymentline(line) {        
        console.log(line);
        var voucher_id = line.voucherId;
        if(voucher_id){
            await this.pos.orm.write("pos.voucher",[voucher_id],{state: 'open'});
        }        
        super.remove_paymentline(line);        
    },
    // Start POS Promotion
    apply_pos_promotion(product){
        console.log('Apply POS Promotion');        
        for(var promotion of this.pos.pos_promotions){
            let promotion_type = promotion.promotion_type;
            let flag = false;
            switch (promotion_type) {
                case 'buy_x_get_y':
                    console.log('buy_x_get_y');
                    if (promotion.is_member){                                                    
                        this.apply_buy_x_get_y_promotion(promotion);                        
                    }else{
                        this.apply_buy_x_get_y_promotion(promotion);
                    }
                    break;
                case 'buy_x_get_dis_y':
                    console.log('buy_x_disc_y');
                    break;
            }
        }
    },
    check_for_valid_promotion(promotion){
        console.log("Check for valid promotion");                    
        var from_date = new Date(promotion.from_date + ' 00:00:00');
        var to_date = new Date(promotion.to_date + ' 23:59:00');                                                  
        var current_date = new Date().getTime();
        if (current_date > from_date && current_date < to_date){
            console.log("Promotion Valid");                    
            return true;
        }else{
            console.log("Promotion not Valid");                    
            return false;
        }
    },    
    get_orderline_by_unique_id(uniqueId){
        var orderlines = this.orderlines;
        for(var i = 0; i < orderlines.length; i++){
            if(orderlines[i].uniqueChildId === uniqueId){
                return orderlines[i];
            }
        }
        return null;
    },
    update_promotion_line(promotion, product_y_id, qty){
        var self = this;
        console.log('update_promotion_line');
        let promo_product = this.pos.db.get_product_by_id(product_y_id);
        var currentOrderLine = this.get_selected_orderline();            
        var new_line = new Orderline({env: this.env}, {pos: this.pos, order: this.pos.get_order(), product: promo_product});
        new_line.set_quantity(qty);
        new_line.price_manually_set = true;
        new_line.set_unit_price(0);                    
        new_line.set_unique_child_id(currentOrderLine.get_unique_parent_id());
        new_line.set_promotion(promotion);            
        this.pos.get_order().add_orderline(new_line);        
        this.select_orderline(currentOrderLine);
    },  
    async removeOrderline(orderline){
        console.log(orderline);
        if(orderline.uniqueParentId || orderline.uniqueChildId){
            if(orderline.uniqueParentId){
                var matchPromotionOrderlines = this.get_orderlines().filter(function(line){
                    if(line.get_unique_child_id() == orderline.uniqueParentId){
                        return line;
                    }
                });
                console.log("matchPromotionOrderlines");
                console.log(matchPromotionOrderlines);
                for(const line of matchPromotionOrderlines){  
                    super.removeOrderline(line);
                }                
                super.removeOrderline(...arguments);
            }else if (orderline.uniqueChildId){
                console.log("Delete this item not allowed");
                // await this.popup.add(ErrorPopup, {
                //     title: _t("Promotion Error"),
                //     body: _t("Delete this item not allowed"),
                // });
            }else{            
                super.removeOrderline(...arguments);
            }
        }else{
            super.removeOrderline(...arguments);
        }        
    },
    async apply_buy_x_get_y_promotion(promotion){
        if(!this.check_for_valid_promotion(promotion))
            return;

        var selectedOrderLine = this.get_selected_orderline();
        console.log(promotion.pos_condition_ids);
        if(selectedOrderLine && promotion.pos_condition_ids.length > 0){            
            for(const pos_condition_id of promotion.pos_condition_ids){
                var pos_condition = this.pos.pos_conditions_by_id[pos_condition_id];
                if(selectedOrderLine.product.id === pos_condition.product_x_id[0]){
                    if(selectedOrderLine.quantity >= pos_condition.quantity){
                        if(selectedOrderLine && !selectedOrderLine.get_unique_parent_id()){
                            selectedOrderLine.set_unique_parent_id(Math.floor(Math.random() * 1000000000));
                            // selectedOrderLine.set_promotion(promotion); 
                            selectedOrderLine.price_manually_set = true;
                            // selectedOrderLine.set_allow_merge(false);
                            var parentId = await selectedOrderLine ? selectedOrderLine.get_unique_parent_id() : false;
                            var childOrderLine = this.get_orderline_by_unique_id(parentId ? selectedOrderLine.get_unique_parent_id() : false);
                            this.update_promotion_line(promotion, pos_condition.product_y_id[0],  pos_condition.quantity_y);    
                        }
                    }
                    break;
                }
            }
        }
    },
    //End POS Promotion
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        // Pos Deposit
        this.is_deposit_order = json.is_deposit_order;
        // Pos Promotion
        this.orderPromotion = json.orderPromotion;
        this.orderDiscountLine = json.orderDiscountLine;
    },    
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        // Pos Deposit
        json.is_deposit_order = this.is_deposit_order
        // Pos Promotion
        json.orderPromotion = this.orderPromotion || false;
        json.orderDiscountLine = this.orderDiscountLine || false;
        return json;
    },
    clone(){
        const order = super.clone(...arguments);
        order.is_deposit_order = json.is_deposit_order
        return order;
    },

});


patch(Orderline.prototype, {
    setup(_defaultObj, options) {        
        super.setup(...arguments);
        //Promotion
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
    },
    set_allow_merge(allowMerge){
        this.allowMerge = allowMerge
    },
    get_allow_merge(){
        return this.allowMerge;
    },
    set_promotion_flag(flag){
        this.promotion_flag = flag;
    },
    get_promotion_flag(){
        return this.promotion_flag;
    },
    set_promotion_disc_parent_id(parentId){
        this.promotion_disc_parentId = parentId;
    },
    get_promotion_disc_parent_id(){
        return this.promotion_disc_parentId;
    },
    set_promotion_disc_child_id(childId){
        this.promotion_disc_childId = childId;
    },
    get_promotion_disc_child_id(){
        return this.promotion_disc_childId;
    },
    set_combination_id(combinationId){
        this.combination_id = combinationId;
    },
    get_combination_id(){
        return this.combination_id;
    },
    set_parent_combination_id(combinationId){
        this.parent_combination_id = combinationId;
    },
    get_parent_combination_id(){
        return this.parent_combination_id;
    },
    //FOR BUY X GET Y FREE PRODUCT START
    set_unique_parent_id(uniqueParentId){
        this.uniqueParentId = uniqueParentId;
    },
    get_unique_parent_id(){
        return this.uniqueParentId;
    },
    set_unique_child_id(uniqueChildId){
        this.uniqueChildId = uniqueChildId;
    },
    get_unique_child_id(){
        return this.uniqueChildId;
    },
    //FOR BUY X GET Y FREE PRODUCT END
    set_promotion(promotion){
        this.promotion = promotion;
    },
    get_promotion(promotion){
        return this.promotion;
    },
    set_is_rule_applied(rule){
        this.applied_rule = rule;
    },
    get_is_rule_applied (){
        return this.applied_rule;
    },
    set_is_promotion_applied(rule){
        this.is_promotion_applied = rule;
    },
    get_is_promotion_applied(){
        return this.is_promotion_applied;
    },
    set_buy_x_get_dis_y(product_ids){
        this.product_ids = product_ids;
    },
    get_buy_x_get_dis_y(){
        return this.product_ids;
    },
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
    },
    export_for_printing() {
        var line = super.export_for_printing(...arguments);
        line.promotion_code = this.promotion ? this.promotion.promotion_code : '';
        line.promotion_description = this.promotion ? this.promotion.promotion_description : '';  
        console.log("export_for_printing");
        console.log(line);              
        return line;
    },
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
    },    
    init_from_JSON(json){
        super.init_from_JSON(...arguments);
        this.uniqueParentId = json.uniqueParentId;
        this.uniqueChildId = json.uniqueChildId;
        this.isRuleApplied = json.isRuleApplied;
        this.promotion = json.promotion;
        this.promotion_flag = json.promotion_flag;
        this.promotion_disc_parentId = json.promotion_disc_parentId;
        this.promotion_disc_childId = json.promotion_disc_childId;
    },

});

register_payment_method("deposit", PaymentDeposit);

patch(Payment.prototype, {
    //@override
    setup() {
        super.setup(...arguments);
        this.terminalServiceId = this.terminalServiceId || null;
        this.isVoucherPayment = this.isVoucherPayment || false;
        this.voucherId = this.voucherId || false;
        this.voucherAmount = this.voucherAmount || 0;
    },
    set_is_voucher_payment(value){
        this.isVoucherPayment = value;
    },
    get_is_voucher_payment(){
        return this.isVoucherPayment;
    },
    set_voucher_id(voucherId){
        this.voucherId = voucherId;
    },
    get_voucher_id(){
        return this.voucherId;
    },
    set_voucher_amount(voucherAmount){
        this.voucherAmount = voucherAmount;
    },
    get_voucher_amount(){
        return this.voucherAmount;
    },
    //@override
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        if (json) {
            json.terminal_service_id = this.terminalServiceId;
            json.isVoucherPayment = this.isVoucherPayment;
            json.voucherId = this.voucherId;
            json.voucherAmount = this.voucherAmount;
        }
        return json;
    },
    //@override
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.terminalServiceId = json.terminal_service_id;
        this.isVoucherPayment = json.isVoucherPayment;
        this.voucherId = json.voucherId;
        this.voucherAmount = json.voucherAmount;
    },
    setTerminalServiceId(id) {
        this.terminalServiceId = id;
    },
});