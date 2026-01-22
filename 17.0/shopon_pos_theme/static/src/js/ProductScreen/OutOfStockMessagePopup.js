odoo.define("shopon_pos_theme.popups", function (require) {
  "use strict";
  const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
  const Registries = require("point_of_sale.Registries");

  class OutOfStockMessagePopup extends AbstractAwaitablePopup {}
  OutOfStockMessagePopup.template = "OutOfStockMessagePopup";
  OutOfStockMessagePopup.defaultProps = { title: "Confirm ?", body: "" };
  Registries.Component.add(OutOfStockMessagePopup);

  return OutOfStockMessagePopup;
});