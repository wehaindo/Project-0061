odoo.define('weha_smart_pos_aeon_pos_access_rights.HeaderLockButton', function(require) {
    'use strict';

    const HeaderLockButton = require('point_of_sale.HeaderLockButton');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, useState } = owl;
    const PosActivityLog = require('weha_smart_pos_aeon_activity_log.PosActivityLog');

    const PosAccessRightsHeaderLockButton = (HeaderLockButton) => 
        class extends HeaderLockButton {
            setup(){
                super.setup();
                this.posActivityLog = new PosActivityLog();
            }

            async showLoginScreen() {
                console.log('showLoginScreen')
                var order = this.env.pos.get_order()
                this.posActivityLog.saveLogToLocalStorage(
                    'Product Screen',
                    'Logout',
                    this.env.pos.user.id,
                    order.cashier.id,
                    this.env.pos.config.id,
                    this.env.pos.pos_session.id,
                    order.cashier.name
                );
                await super.showLoginScreen();                
            }
        }
    
    Registries.Component.extend(HeaderLockButton, PosAccessRightsHeaderLockButton);        

});