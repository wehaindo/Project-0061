odoo.define('weha_smart_pos_rest.FloorScreen', function (require) {
    'use strict';

    const FloorScreen = require('pos_restaurant.FloorScreen');
    const Registries = require('point_of_sale.Registries');
    const { debounce } = require("@web/core/utils/timing");
    const { isConnectionError } = require('point_of_sale.utils');

    const { onPatched, onMounted, onWillUnmount, useRef, useState } = owl;

    const RestFloorScreen = (FloorScreen) => 
    class extends FloorScreen {
        setup() {
            super.setup();
            onPatched(this.onPatched);
            onMounted(this.onMounted);
        }

        onPatched() {            
            this.floorMapRef.el.style.backgroundImage = "url('https://upload.wikimedia.org/wikipedia/commons/9/9a/Sample_Floorplan.jpg')";            
            this.floorMapRef.el.style.backgroundSize = "auto";
            this.floorMapRef.el.style.backgroundPosition = "center";
        }
        
        onMounted() {            
            this.floorMapRef.el.style.backgroundImage = "url('https://upload.wikimedia.org/wikipedia/commons/9/9a/Sample_Floorplan.jpg')";            
            this.floorMapRef.el.style.backgroundSize = "auto";
            this.floorMapRef.el.style.backgroundPosition = "center";
        }
    }

    Registries.Component.extend(FloorScreen, RestFloorScreen);
});