/** @odoo-module **/

import { Gui } from 'point_of_sale.Gui';
import PosComponent from 'point_of_sale.PosComponent';
import ProductScreen from 'point_of_sale.ProductScreen';
import Registries from 'point_of_sale.Registries';
import { useListener } from "@web/core/utils/hooks";


export class DeleteUnpaidOrdersButton extends PosComponent {
    setup() {
        super.setup();
        useListener('click', this.onClick);
    }

    async onClick(){
        const { confirmed } = await this.showPopup('ConfirmPopup', {
            title: this.env._t('Delete Unpaid Orders ?'),
            body: this.env._t(
                'This operation will destroy all unpaid orders in the browser. You will lose all the unsaved data and exit the point of sale. This operation cannot be undone.'
            ),
        });
        if (confirmed) {
            this.env.pos.db.remove_all_unpaid_orders();
            window.location = '/';
        }
    }
}

DeleteUnpaidOrdersButton.template = 'DeleteUnpaidOrdersButton';

ProductScreen.addControlButton({
    component: DeleteUnpaidOrdersButton,
    condition: function() {
        return this.env.pos.config.is_allow_delete_unpaid_order;
    }
});

Registries.Component.add(DeleteUnpaidOrdersButton);
