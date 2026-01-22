odoo.define('weha_smart_pos_access_rights.LoginScreen', function (require) {
    'use strict';

    const LoginScreen = require('pos_hr.LoginScreen');
    const Registries = require('point_of_sale.Registries');
    const { onMounted, useRef, useState } = owl;


    const PosAccessRightsLoginScreen = (LoginScreen) => 
        class extends LoginScreen {
            setup(){
                super.setup();
            }

            async selectCashier() {
                console.log("Select Cashier 1");
            }

        }       

    Registries.Component.extends(LoginScreen, PosAccessRightsLoginScreen);        
});