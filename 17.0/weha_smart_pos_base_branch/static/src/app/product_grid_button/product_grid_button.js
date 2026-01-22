/** @odoo-module */

import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";
import { Navbar } from "@point_of_sale/app/navbar/navbar";

export class ProductGridButton extends Component {
    static template = "weha_smart_pos_base.ProductGridButton";

    setup() {
        this.pos = usePos();
        this.ui = useState(useService("ui"));
    }

    async showToggleProductGrid() {
        console.log("Click showToggleProductGrid");
        this.pos.config.is_show_product_grid = !this.pos.config.is_show_product_grid;
    }
}


Navbar.components = { ...Navbar.components,ProductGridButton };