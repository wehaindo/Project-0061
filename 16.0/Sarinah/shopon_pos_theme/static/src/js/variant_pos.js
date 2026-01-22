odoo.define('shopon_pos_theme.variant_pos', function (require, factory) {
    'use strict';

    const Registries = require("point_of_sale.Registries");
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
	const { useListener, useBus } = require("@web/core/utils/hooks");
    const { useRef, onPatched, onMounted, useState } = owl;

    var utils = require('web.utils');


    class ShopOnVariantPopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
            useListener('click-product', this._clickProduct1);
            useBus(this.env.posbus, 'close-popup', this._closePopup);
            onMounted(() => {
                if (this.env.pos.config.setu_pos_variants_group_by_attribute && !this.env.pos.config.setu_pos_display_alternative_products) {
                    $('.main').addClass('setu_product_attr_no_alternative')
                    $('.setu_product_variants_popup').addClass('setu_attr_no_alternative_popup')
                }
                if (this.Attribute_names && this.Attribute_names.length > 0 && this.AlternativeProducts && this.AlternativeProducts < 1) {
                    $('.main').addClass('setu_only_attributes')
                }
            })
        }
        updateSearch(event) {
            this.searchWord = event.target.value;
            this.render()
        }
        async _clickProduct1(event) {
            var product = event.detail
            var currentOrder = this.env.pos.get_order()
            await currentOrder.add_product(product)
            if (this.env.pos.config.setu_close_popup_after_single_selection) {
                $('.button.cancel').trigger('click')
            }
        }
        Confirm() {
            var self = this
            var lst = []
            var currentOrder = this.env.pos.get_order()
            if ($('#attribute_value.highlight')) {
                _.each($('#attribute_value.highlight'), function (each) {
                    lst.push(parseInt($(each).attr('data-id')))
                })
            }
            _.each(self.env.pos.db.product_by_id, function (product) {
                if (product.product_template_attribute_value_ids.length > 0 && JSON.stringify(product.product_template_attribute_value_ids) === JSON.stringify(lst)) {
                    currentOrder.add_product(product)
                }
            })
            if (this.props.attributes_name.length > $('.highlight').length) {
                alert('Please Select Variant')
            } else {
                if (self.env.pos.config.setu_close_popup_after_single_selection) {
                    this.trigger("close-popup");
                } else {
                    $('.setu_group_by_attribute').find('.highlight').removeClass('highlight')
                }
            }
        }
        get VariantProductToDisplay() {
            if (this.searchWord) {
                return this.env.pos.db.search_variants(this.props.product_variants, this.searchWord);
            } else {
                return this.props.product_variants;
            }
        }
        get Attribute_names() {
            return this.props.attributes_name
        }
        check_has_valid_attribute_value(attribute_value){
            if(this.props.product_tmpl_id){
                if(this.env.pos.db && this.env.pos.db.product_attr && this.env.pos.db.product_attr[this.props.product_tmpl_id] && this.env.pos.db.product_attr[this.props.product_tmpl_id].includes(attribute_value)){
                    return true
                }else{
                    return false;
                }
            }else{
                return false;
            }
        }
        get AlternativeProducts() {
            return this.props.alternative_products
        }
        Select_attribute_value(event) {

            _.each($('.' + $(event.currentTarget).attr('class')), function (each) {
                $(each).removeClass('highlight')
            })

            if ($('.setu_attribute_value').hasClass('highlight')) {
                $('.setu_attribute_value').removeClass('highlight')
            }
            if ($(event.currentTarget).hasClass('highlight')) {
                $(event.currentTarget).removeClass('highlight')

            } else {
                $(event.currentTarget).addClass('highlight')
            }
        }
    }
    ShopOnVariantPopup.template = "ShopOnVariantPopup";

    Registries.Component.add(ShopOnVariantPopup);


});
