odoo.define('weha_smart_pos_popup.NumberDenomPopup', function(require) {
    'use strict';
    var core = require('web.core');
    var _t = core._t;

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    const { useState } = owl;

    // formerly NumberPopupWidget
    class NumberDenomPopup extends AbstractAwaitablePopup {
        /**
         * @param {Object} props
         * @param {Boolean} props.isPassword Show password popup.
         * @param {number|null} props.startingValue Starting value of the popup.
         * @param {Boolean} props.isInputSelected Input is highlighted and will reset upon a change.
         *
         * Resolve to { confirmed, payload } when used with showPopup method.
         * @confirmed {Boolean}
         * @payload {String}
         */
        

        setup() {
            super.setup();
            NumberBuffer.INPUT_KEYS = new Set(
                ['Delete', 'Backspace', '+1000', '+2000', '+5000', '+10000', '+20000', '+50000', '+100000'].concat('0123456789+-.,'.split(''))
            );
            useListener('accept-input', this.confirm);
            useListener('close-this-popup', this.cancel);
            let startingBuffer = '';
            if (typeof this.props.startingValue === 'number' && this.props.startingValue > 0) {
                startingBuffer = this.props.startingValue.toString().replace('.', this.decimalSeparator);
            }
            this.state = useState({ buffer: startingBuffer, toStartOver: this.props.isInputSelected });
            NumberBuffer.use({
                nonKeyboardInputEvent: 'numpad-click-input',
                triggerAtEnter: 'accept-input',
                triggerAtEscape: 'close-this-popup',
                state: this.state,
            });
        }
        get decimalSeparator() {
            return this.env._t.database.parameters.decimal_point;
        }
        get inputBuffer() {
            if (this.state.buffer === null) {
                return '';
            }
            if (this.props.isPassword) {
                return this.state.buffer.replace(/./g, '•');
            } else {
                return this.state.buffer;
            }
        }
        confirm(event) {
            if (NumberBuffer.get()) {
                super.confirm();
            }
        }
        sendInput(key) {
            console.log(key);
            this.trigger('numpad-click-input', { key });
        }
        getPayload() {
            return NumberBuffer.get();
        }
    }
    NumberDenomPopup.template = 'NumberDenomPopup';
    NumberDenomPopup.defaultProps = {
        confirmText: _t('Ok'),
        cancelText: _t('Cancel'),
        title: _t('Confirm ?'),
        body: '',
        cheap: false,
        startingValue: null,
        isPassword: false,
    };

    Registries.Component.add(NumberDenomPopup);

    return NumberDenomPopup;
});
