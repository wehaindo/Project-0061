odoo.define('weha_pos.ButtonList', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ControlButtonsMixin = require('point_of_sale.ControlButtonsMixin');
    const Registries = require('point_of_sale.Registries');

    class ButtonList extends ControlButtonsMixin(PosComponent) {}

    ButtonList.template = 'ButtonList';    
    Registries.Component.add(ButtonList);

    return ButtonList;
});