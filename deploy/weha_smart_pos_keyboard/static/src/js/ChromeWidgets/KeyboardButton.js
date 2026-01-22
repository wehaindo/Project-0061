odoo.define('weha_smart_pos_keyboard.KeyboardButton', function(require){
    'use strict';
    
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class KeyboardButton extends PosComponent {
        async onClick() {
            CommandRun.run("C:\\WINDOWS\\system32\\osk.exe", [])
        }
    }

    KeyboardButton.template = 'KeyboardButton';

    Registries.Component.add(KeyboardButton);

    return KeyboardButton;

});