odoo.define('weha_smart_pos_login.Chrome', function(require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");

    const PosLoginChrome = (Chrome) => 
        class extends Chrome {
            setup() {
                super.setup();
                useListener('logout-pos', this._logoutPos);
            }

            async _logoutPos() {
                window.location = '/pos/finger/' + this.env.pos.config.pos_config_code;
            }
        }

    Registries.Component.extend(Chrome, PosLoginChrome);
    return Chrome;
});

