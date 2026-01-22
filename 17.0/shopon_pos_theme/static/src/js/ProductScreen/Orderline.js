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
                if(line_qty < this.env.pos.get_information(this.props.line.product.id) || line_qty == 0 || this.env.pos.config.setu_display_stock == false || this.env.pos.config.setu_continous_sale){
                    this.props.line.quantity += 1
                    this.props.line.set_quantity( this.props.line.quantity, true);
                }
                else{
                    await this.showPopup('ErrorPopup', {
                        title: this.env._t('Warning.'),
                        body: this.env._t("(" + this.props.line.product.display_name + ") " +this.env.pos.config.setu_error_msg + ".")
                    });
                }
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
