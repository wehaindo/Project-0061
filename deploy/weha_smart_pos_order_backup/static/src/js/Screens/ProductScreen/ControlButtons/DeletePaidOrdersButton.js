/** @odoo-module **/

import { Gui } from 'point_of_sale.Gui';
import PosComponent from 'point_of_sale.PosComponent';
import ProductScreen from 'point_of_sale.ProductScreen';
import Registries from 'point_of_sale.Registries';
import { useListener } from "@web/core/utils/hooks";


export class DeletePaidOrdersButton extends PosComponent {
    setup() {
        super.setup();
        useListener('click', this.onClick);
    }

    async onClick(){
        const { confirmed } = await this.showPopup('ConfirmPopup', {
            title: this.env._t('Delete Paid Orders ?'),
            body: this.env._t(
                'This operation will permanently destroy all paid orders from the local storage. You will lose all the data. This operation cannot be undone.'
            ),
        });
        if (confirmed) {
            this.env.pos.db.remove_all_orders();
            this.env.pos.set_synch('connected', 0);
        }
    }
}

DeletePaidOrdersButton.template = 'DeletePaidOrdersButton';

ProductScreen.addControlButton({
    component: DeletePaidOrdersButton,
    condition: function() {
        return this.env.pos.config.is_allow_delete_paid_order;
    }
});

Registries.Component.add(DeletePaidOrdersButton);
