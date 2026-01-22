odoo.define ('shopon_pos_theme.ProductWidgetControlPanel', function (require) {
   'use strict';

   const ProductsWidgetControlPanel = require('point_of_sale.ProductsWidgetControlPanel');
   const Registries = require('point_of_sale.Registries');
    const { qweb } = require('web.core');

    const ShopOnProductsWidgetControlPanelExt = (ProductsWidgetControlPanel) =>
    class extends ProductsWidgetControlPanel {
         async onToggleLayout() {
            if ($('#rightpaneBg').find('.product-list').hasClass('list_view')){
                $('#rightpaneBg').find('.product-list').removeClass('list_view')
            }
            else{
                $('#rightpaneBg').find('.product-list').addClass('list_view')
                $('#grid_view').removeClass('list_view')
            }
            $('#grid_view').toggleClass('d-none');
            $('#list_view').toggleClass('d-none');
        }
        _toggleSideBar(){
            $('.dn_sidebar').toggle(100)
            setTimeout(()=> {
                $('.rightpane-header').scrollTo($('.categories-header'))
            }, 100);

        }
        searchProductFromInfo(productName) {
            if(this.searchWordInput.el){
                super.searchProductFromInfo(productName);
            }
        }
         _toggleMobileSearchbar() {
            setTimeout(()=> {
                $('.rightpane-header').scrollTo($('.categories-header'))
            }, 100);
            super._toggleMobileSearchbar();
        }
    }

    Registries.Component.extend(ProductsWidgetControlPanel,ShopOnProductsWidgetControlPanelExt);
    return ProductsWidgetControlPanel;

});