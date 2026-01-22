odoo.define('weha_smart_pos_aeon_pms.MemberDayIcon', function(require){
    'use strict';
    
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class MemberDayIcon extends PosComponent {
        setup(){
            super.setup();
        }
        
    }

    MemberDayIcon.template = 'MemberDayIcon';

    Registries.Component.add(MemberDayIcon);

    return MemberDayIcon;

});