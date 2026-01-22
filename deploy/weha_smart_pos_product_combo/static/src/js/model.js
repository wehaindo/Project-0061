odoo.define('weha_smart_pos_product_combo.models', function (require) {
    "use strict";

    var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
	var utils = require('web.utils');
	var _t = core._t;
    var round_di = utils.round_decimals;
	var round_pr = utils.round_precision;

    const ProductComboPosGlobalState = (PosGlobalState) => 
        class  extends PosGlobalState {
            setup(obj){
                super.setup(...arguments)
            }

            async _processData(loadedData) {
                await super._processData(...arguments);
                this.pos_product_pack = loadedData['product.pack'];
                // await this.loadProductPack();

            }

            loadProductPack(){
                this.pos_product_pack = {};
                for(const pack of this.pos_product_packs){
                    this.pos_product_pack[pack.id] = pack;
                };
            }
        }

    
    Registries.Model.extend(PosGlobalState, ProductComboPosGlobalState);

    const ProductComboOrderLine = (Orderline) => 
        class extends Orderline {
            setup(obj, options) {
                super.setup(...arguments);
                this.pos   = options.pos;
                this.order = options.order;
                var self = this;
                if (options.json) {
                    this.init_from_JSON(options.json);
                    return;
                }
                this.combo_products = this.combo_products;

                var final_data = self.pos.get('final_products')
                if(final_data)
                {
                    for (var i = 0; i < final_data.length; i++) {
                        if(final_data[i][0] == this.product.id)
                        {
                            this.combo_products = final_data[i][1];
                            self.pos.set({
                                'final_products': null,
                            });
                        }
                    }
                }
                
                this.set_combo_products(this.combo_products);
                this.combo_prod_ids =  this.combo_prod_ids || [];
                this.is_pack = this.is_pack;
            }

            clone(){
                var orderline = Orderline.create({},{
                    pos: this.pos,
                    order: this.order,
                    product: this.product,
                    price: this.price,
                });
                orderline.order = null;
                orderline.combo_prod_ids = this.combo_prod_ids || [];
                orderline.combo_products = this.combo_products || [];
                orderline.quantity = this.quantity;
                orderline.quantityStr = this.quantityStr;
                orderline.discount = this.discount;
                orderline.price = this.price;
                orderline.type = this.type;
                orderline.selected = false;
                orderline.is_pack = this.is_pack;
                orderline.price_manually_set = this.price_manually_set;
                return orderline;
            }

            init_from_JSON(json) {
                super.init_from_JSON(...arguments);                
                this.combo_prod_ids = json.combo_prod_ids;
                this.is_pack = json.is_pack;
            }
    
            export_as_JSON(){
                var json = super.export_as_JSON(...arguments);
                json.combo_products = this.get_combo_products();
                json.combo_prod_ids= this.combo_prod_ids;
                json.is_pack=this.is_pack;
                return json;
            }
    
            export_for_printing(){
                var json = super.export_for_printing(...arguments);
                json.combo_products = this.get_combo_products();
                json.combo_prod_ids= this.combo_prod_ids;
                json.is_pack=this.is_pack;
                return json;
            }

            set_combo_prod_ids(ids){
                this.combo_prod_ids = ids
                // this.trigger('change',this);
            }

            set_combo_products(products) {
                var ids = [];
                if(this.product.is_pack)
                {	
                    if(products)
                    {
                        products.forEach(function (prod) {
                            if(prod != null)
                            {
                                ids.push(prod.id)
                            }
                        });
                    }
                    this.combo_products = products;
                    this.set_combo_prod_ids(ids)
                    if(this.combo_prod_ids)
                    {
                        this.set_combo_price(this.price);
                    }
                    // this.trigger('change',this);
                }   
            }

            set_is_pack(is_pack){
                this.is_pack = is_pack
                // this.trigger('change',this);
            }

            set_unit_price(price){
                var self = this;
                this.order.assert_editable();
                if(this.product.is_pack)
                {
                    this.set_is_pack(true);
                    var prods = this.get_combo_products()
                    var total = price;
                
                    this.price = round_di(parseFloat(total) || 0, this.pos.dp['Product Price']);
                }
                else{
                    this.price = round_di(parseFloat(price) || 0, this.pos.dp['Product Price']);
                }
                // this.trigger('change',this);
            }

            set_combo_price(price){
                var prods = this.get_combo_products()
                var total = 0;
                prods.forEach(function (prod) {
                    if(prod)
                    {
                        total += prod.lst_price	
                    }	
                });
                if(self.pos.config.combo_pack_price== 'all_product'){
                    this.set_unit_price(total);
                }
                else{
                    let prod_price = this.product.lst_price;
                    this.set_unit_price(prod_price);
                }
                // this.trigger('change',this);
            }

            get_combo_products() {
                self = this;
                if(this.product.is_pack)
                {
                    var get_sub_prods = [];
                    if(this.combo_prod_ids)
                    {
                        this.combo_prod_ids.forEach(function (prod) {
                            var sub_product = self.pos.db.get_product_by_id(prod);
                            get_sub_prods.push(sub_product)
                        });
                        return get_sub_prods;
                    }
                    if(this.combo_products)
                    {
                        if(! null in this.combo_products){
                            return this.combo_products
                        }
                    }
                }
            }
        }


    Registries.Model.extend(Orderline, ProductComboOrderLine);

    const ProductComboOrder = (Order) => 
        class extends Order {
            constructor(obj, options) {
                super(...arguments)
                this.barcode = this.barcode || "";
            }

            build_line_resume(){
                var resume = {};
                this.orderlines.each(function(line){
                    if (line.mp_skip) {
                        return;
                    }
                    var qty  = Number(line.get_quantity());
                    var note = line.get_note();
                    var product_id = line.get_product().id;
                    var product_name = line.get_full_product_name();
                    var p_key = product_id + " - " + product_name;
                    var product_resume = p_key in resume ? resume[p_key] : {
                        pid: product_id,
                        product_name_wrapped: line.generate_wrapped_product_name(),
                        qties: {},
                    };
                    if (note in product_resume['qties']) product_resume['qties'][note] += qty;
                    else product_resume['qties'][note] = qty;
                    resume[p_key] = product_resume;
                    var combo_list = []
                    if(line.combo_prod_ids && line.combo_prod_ids.length > 0){
                        var combo = line.get_combo_products();
                        combo.forEach(function(prd){
                            combo_list.push(prd.display_name)
                        })
                    }
                    resume['combo'] = combo_list
                });
                return resume;
            }

            saveChanges(){
                this.saved_resume = this.build_line_resume();
                this.orderlines.each(function(line){
                    line.set_dirty(false);
                });
                // this.trigger('change',this);
            }

            computeChanges(categories){
                var resume = posorder_super.computeChanges.apply(this,arguments, categories);
                var current_res = this.build_line_resume();
                var old_res     = this.saved_resume || {};
                var json        = this.export_as_JSON();
                var add = [];
                var rem = [];
                var p_key, note;
    
                for (p_key in current_res) {
                    for (note in current_res[p_key]['qties']) {
                        var curr = current_res[p_key];
                        var old  = old_res[p_key] || {};
                        var pid = curr.pid;
                        var found = p_key in old_res && note in old_res[p_key]['qties'];
    
                        if (!found) {
                            add.push({
                                'id':       pid,
                                'name':     this.pos.db.get_product_by_id(pid).display_name,
                                'name_wrapped': curr.product_name_wrapped,
                                'note':     note,
                                'current_res': current_res.combo,
                                'qty':      curr['qties'][note],
                            });
                        } else if (old['qties'][note] < curr['qties'][note]) {
                            add.push({
                                'id':       pid,
                                'name':     this.pos.db.get_product_by_id(pid).display_name,
                                'name_wrapped': curr.product_name_wrapped,
                                'note':     note,
                                'current_res': current_res.combo,
                                'qty':      curr['qties'][note] - old['qties'][note],
                            });
                        } else if (old['qties'][note] > curr['qties'][note]) {
                            rem.push({
                                'id':       pid,
                                'name':     this.pos.db.get_product_by_id(pid).display_name,
                                'name_wrapped': curr.product_name_wrapped,
                                'note':     note,
                                'current_res': current_res.combo,
                                'qty':      old['qties'][note] - curr['qties'][note],
                            });
                        }
                    }
                }
    
                for (p_key in old_res) {
                    for (note in old_res[p_key]['qties']) {
                        var found = p_key in current_res && note in current_res[p_key]['qties'];
                        if (!found) {
                            var old = old_res[p_key];
                            var pid = old.pid;
                            rem.push({
                                'id':       pid,
                                'name':     this.pos.db.get_product_by_id(pid).display_name,
                                'name_wrapped': old.product_name_wrapped,
                                'note':     note,
                                'current_res': current_res.combo,
                                'qty':      old['qties'][note],
                            });
                        }
                    }
                }
    
                if(categories && categories.length > 0){
                    // filter the added and removed orders to only contains
                    // products that belong to one of the categories supplied as a parameter
    
                    var self = this;
    
                    var _add = [];
                    var _rem = [];
    
                    for(var i = 0; i < add.length; i++){
                        if(self.pos.db.is_product_in_category(categories,add[i].id)){
                            _add.push(add[i]);
                        }
                    }
                    add = _add;
    
                    for(var i = 0; i < rem.length; i++){
                        if(self.pos.db.is_product_in_category(categories,rem[i].id)){
                            _rem.push(rem[i]);
                        }
                    }
                    rem = _rem;
                }
    
                var d = new Date();
                var hours   = '' + d.getHours();
                    hours   = hours.length < 2 ? ('0' + hours) : hours;
                var minutes = '' + d.getMinutes();
                    minutes = minutes.length < 2 ? ('0' + minutes) : minutes;
    
                return {
                    'new': add,
                    'cancelled': rem,
                    'table': json.table || false,
                    'floor': json.floor || false,
                    'name': json.name  || 'unknown order',
                    'time': {
                        'hours':   hours,
                        'minutes': minutes,
                    },
                };
    
            }

            hasChangesToPrint(){
                var printers = this.pos.printers;
                for(var i = 0; i < printers.length; i++){
                    var changes = this.computeChanges(printers[i].config.product_categories_ids);
                    if ( changes['new'].length > 0 || changes['cancelled'].length > 0){
                        return true;
                    }
                }
                return false;
            }

            hasSkippedChanges() {
                var orderlines = this.get_orderlines();
                for (var i = 0; i < orderlines.length; i++) {
                    if (orderlines[i].mp_skip) {
                        return true;
                    }
                }
                return false;
            }
        }

    
    Registries.Model.extend(Order, ProductComboOrder);

});