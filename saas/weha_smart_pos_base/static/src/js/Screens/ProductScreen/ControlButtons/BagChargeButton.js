odoo.define('weha_smart_pos_base.BagChargeButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class BagChargeButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        get currentOrder() {
            return this.env.pos.get_order();
        }

        async onClick() {
            var bagproducts = this.env.pos.db.get_product_by_category(this.env.pos.config.bag_pos_category_id[0]);
            const selectionList = bagproducts.map(bagproduct => ({
                id: bagproduct.id,
                label: bagproduct.display_name,
                isSelected: false,
                item: bagproduct,
            }));
            const { confirmed, payload: selectedProduct } = await this.showPopup(
                'SelectionPopup',
                {
                    title: this.env._t('Select the Bag Product'),
                    list: selectionList,
                }
            );
            if (confirmed) {
                this.currentOrder.add_product(selectedProduct, {
                    quantity: 1,
                });
            }
        }
    }
    BagChargeButton.template = 'BagChargeButton';

    ProductScreen.addControlButton({
        component: BagChargeButton,
        condition: function() {
            return this.env.pos.config.is_show_bag_charge
        },
    });

    Registries.Component.add(BagChargeButton);

    return BagChargeButton;
});