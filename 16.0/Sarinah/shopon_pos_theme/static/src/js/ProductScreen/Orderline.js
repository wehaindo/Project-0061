odoo.define('shopon_pos_theme.Orderline', function(require) {
    'use strict';

    const Orderline = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');
    const { Gui } = require("point_of_sale.Gui");
    var core = require("web.core");
    var _t = core._t;

    const ShopOnOrderline = Orderline =>
        class extends Orderline {
            async onPlusButtonClicked() {
                var line_qty = this.props.line.quantity                
                this.props.line.quantity += 1
                this.props.line.set_quantity( this.props.line.quantity, true);                
            }
            async onMinusButtonClicked(){
                this.props.line.quantity -= 1
                this.props.line.set_quantity( this.props.line.quantity, true);
            }
            async onDeleteOrderLine(){
                this.trigger('numpad-click-input', { key: 'Backspace' });
                this.trigger('numpad-click-input', { key: 'Backspace' });
            }
        };

    Registries.Component.extend(Orderline, ShopOnOrderline);

    return Orderline;
});
