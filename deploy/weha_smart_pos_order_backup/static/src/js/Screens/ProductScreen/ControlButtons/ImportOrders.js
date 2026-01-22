/** @odoo-module **/

import { Gui } from 'point_of_sale.Gui';
import PosComponent from 'point_of_sale.PosComponent';
import ProductScreen from 'point_of_sale.ProductScreen';
import Registries from 'point_of_sale.Registries';
import { useListener } from "@web/core/utils/hooks";

export class ImportOrdersButton extends PosComponent {
    setup() {
        super.setup();
        useListener('click', this.onClick);
    }

    async onClick(){
        await this.showPopup('ImportOrdersPopup');
    }
}

ImportOrdersButton.template = 'ImportOrdersButton';

ProductScreen.addControlButton({
    component: ImportOrdersButton,
    condition: function() {
        return this.env.pos.config.is_allow_import_order;
    }
});

Registries.Component.add(ImportOrdersButton);
