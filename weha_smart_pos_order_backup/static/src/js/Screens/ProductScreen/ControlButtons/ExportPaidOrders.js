/** @odoo-module **/

import { Gui } from 'point_of_sale.Gui';
import PosComponent from 'point_of_sale.PosComponent';
import ProductScreen from 'point_of_sale.ProductScreen';
import Registries from 'point_of_sale.Registries';
import { useListener } from "@web/core/utils/hooks";


export class ExportPaidOrdersButton extends PosComponent {
    setup() {
        super.setup()
        useListener('click', this.onClick);
    }
    
    async onClick(){
        await this.showPopup('ExportPaidOrdersPopup');
    }
}

ExportPaidOrdersButton.template = 'ExportPaidOrdersButton';

ProductScreen.addControlButton({
    component: ExportPaidOrdersButton,
    condition: function() {
        return this.env.pos.config.is_allow_export_paid_order;
    }
});

Registries.Component.add(ExportPaidOrdersButton);
