odoo.define("sh_pos_order_list.screen_exchange", function (require) {
    "use strict";

    const { debounce } = owl.utils;
    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");
    const { useListener } = require("web.custom_hooks");
    const rpc = require("web.rpc");
    var core = require("web.core");
    var framework = require("web.framework");
    var QWeb = core.qweb;
    const PaymentScreen = require("point_of_sale.PaymentScreen");
    var field_utils = require("web.field_utils");
    const OrderListScreen = require("sh_pos_order_list.screen");

    const PosOrderListScreen = (OrderListScreen) =>
        class extends OrderListScreen {

            get_order_by_name(name) {
                var self = this;
                if (self.return_filter) {
                    return _.filter(self.env.pos.db.all_return_order, function (template) {
                        if (template.name.indexOf(name) > -1) {
                            return true;
                        } else if (template["pos_reference"].indexOf(name) > -1) {
                            return true;
                        } else if (template["partner_id"] && template["partner_id"][1] && template["partner_id"][1].toLowerCase().indexOf(name) > -1) {
                            return true;
                        } else if (template["date_order"].indexOf(name) > -1) {
                            return true;
                        } else {
                            return false;
                        }
                    });
                } else {
                    return _.filter(self.env.pos.db.all_order, function (template) {
                        if (template.name.indexOf(name) > -1) {
                            return true;
                        } else if (template["pos_reference"].indexOf(name) > -1) {
                            return true;
                        } else if (template["partner_id"] && template["partner_id"][1] && template["partner_id"][1].toLowerCase().indexOf(name) > -1) {
                            return true;
                        } else if (template["date_order"].indexOf(name) > -1) {
                            return true;
                        } else {
                            return false;
                        }
                    });
                }

            }
            get posorderdetailhistory() {
                return super.posorderdetailhistory()
            }
            updateOrderList(event) {
                this.state.query = event.target.value;

                if (event.code === "Enter") {
                    const serviceorderlistcontents = this.posreturnorderdetail;
                    if (serviceorderlistcontents.length === 1) {
                        this.state.selectedQuotation = serviceorderlistcontents[0];
                    }
                } else {
                    this.render();
                }
            }
            get posreturnorderdetail() {
                var self = this;

                if (this.state.query && this.state.query.trim() !== "") {
                    var templates = this.get_order_by_name(this.state.query.trim());
                    return templates;
                } else {
                    self.order_no_return = [];
                    self.return_order = [];
                    _.each(self.all_order, function (order) {
                        if ((order.is_return_order && order.return_status && order.return_status != "nothing_return") || (!order.is_return_order && !order.is_exchange_order)) {
                            self.order_no_return.push(order);
                        } else {
                            self.return_order.push(order);
                        }
                    });

                    if (!self.return_filter) {
                        return self.order_no_return;
                    } else {
                        return self.return_order;
                    }
                }
            }
            return_order_filter() {
                var self = this;

                if (self.env.pos.get_order().is_client_order_filter) {
                    if (!$(".return_order_button").hasClass("highlight")) {
                        self.order_no_return = [];
                        $(".return_order_button").addClass("highlight");
                        self.return_filter = true;
                        $('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.db.display_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                        $('.sh_pagination').pagination('selectPage', 1);
                    } else {
                        self.return_order = [];
                        $(".return_order_button").removeClass("highlight");
                        self.return_filter = false;
                        $('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.db.display_non_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                        $('.sh_pagination').pagination('selectPage', 1);
                    }
                } else {
                    var previous_order = self.env.pos.db.all_order;
                    if (!$(".return_order_button").hasClass("highlight")) {
                        self.order_no_return = [];
                        $(".return_order_button").addClass("highlight");

                        self.return_filter = true;
                        $('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.db.all_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                        $('.sh_pagination').pagination('selectPage', 1);
                    } else {
                        self.return_order = [];
                        $(".return_order_button").removeClass("highlight");
                        self.return_filter = false;
                        $('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.db.all_non_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                        $('.sh_pagination').pagination('selectPage', 1);
                    }
                }


                self.render();
            }
            exchange_pos_order(event) {
                var self = this;
                self.env.pos.is_return = false;
                self.env.pos.is_exchange = true;

                var order_line = [];
                var order_id = event.currentTarget.closest("tr").attributes[0].value;
                if (order_id) {
                    var order_data = self.env.pos.db.order_by_uid[order_id];
                    if (!order_data) {
                        order_data = self.env.pos.db.order_by_id[order_id];
                    }
                    if (order_data && order_data.lines) {
                        _.each(order_data.lines, function (each_order_line) {
                            var line_data = self.env.pos.db.order_line_by_id[each_order_line];
                            if (!line_data) {
                                line_data = self.env.pos.db.order_line_by_uid[each_order_line[2].sh_line_id];
                            }
                            if (line_data) {
                                order_line.push(line_data);
                            }
                        });
                    }
                }

                let { confirmed, payload } = this.showPopup("TemplateReturnOrderPopupWidget", { lines: order_line, order: order_id });
                if (confirmed) {
                } else {
                    return;
                }
            }
            return_pos_order(event) {
                var self = this;
                self.env.pos.is_return = true;
                self.env.pos.is_exchange = false;
                var order_line = [];
                var order_id = event.currentTarget.closest("tr").attributes[0].value;
                if (order_id) {
                    var order_data = self.env.pos.db.order_by_uid[order_id];
                    if (!order_data) {
                        order_data = self.env.pos.db.order_by_id[order_id];
                    }
                    if (order_data && order_data.lines) {
                        _.each(order_data.lines, function (each_order_line) {
                            var line_data = self.env.pos.db.order_line_by_id[each_order_line];
                            if (!line_data) {
                                line_data = self.env.pos.db.order_line_by_uid[each_order_line[2].sh_line_id];
                            }
                            if (line_data) {
                                order_line.push(line_data);
                            }
                        });
                    }
                }
                let { confirmed, payload } = this.showPopup("TemplateReturnOrderPopupWidget", { lines: order_line, order: order_id });
                if (confirmed) {
                } else {
                    return;
                }
            }
            mounted() {
                var self = this;
                if (self.env.pos.get_order().is_client_order_filter) {
                    $(".sh_pagination").pagination({
                        pages: 100,
                        displayedPages: 1,
                        edges: 1,
                        cssStyle: "light-theme",
                        showPageNumbers: false,
                        showNavigator: true,
                        onPageClick: function (pageNumber) {

                            self.env.pos.db.display_return_order = []
                            self.env.pos.db.display_non_return_order = []
                            var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(pageNumber) - 1);
                            var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page);

                            _.each(self.env.pos.db.all_display_order_temp, function (each_order) {
                                if (each_order) {
                                    if (each_order.is_return_order) {
                                        self.env.pos.db.display_return_order.push(each_order)
                                    } else {
                                        self.env.pos.db.display_non_return_order.push(each_order)
                                    }
                                }
                            })

                            if (self.return_filter) {
                                self.env.pos.db.display_all_order = self.env.pos.db.display_return_order.slice(showFrom, showTo)
                            } else {
                                self.env.pos.db.display_all_order = self.env.pos.db.display_non_return_order.slice(showFrom, showTo)
                            }
                            self.render()
                        }
                    });

                } else {
                    $(".sh_pagination").pagination({
                        pages: 100,
                        displayedPages: 1,
                        edges: 1,
                        cssStyle: "light-theme",
                        showPageNumbers: false,
                        showNavigator: true,
                        onPageClick: function (pageNumber) {

                            try {
                                if (!self.return_filter) {

                                    rpc.query({
                                        model: "pos.order",
                                        method: "search_return_order",
                                        args: [self.env.pos.config, pageNumber + 1]
                                    }).then(function (orders) {
                                        if (orders) {
                                            if (orders['order'].length == 0) {
                                                $($('.next').parent()).addClass('disabled')
                                                $(".next").replaceWith(function () {
                                                    $("<span class='current next'>Next</span>");
                                                });
                                            }
                                        }

                                    }).catch(function (reason) {

                                    });

                                    rpc.query({
                                        model: "pos.order",
                                        method: "search_return_order",
                                        args: [self.env.pos.config, pageNumber]
                                    }).then(function (orders) {
                                        self.env.pos.db.all_order = [];
                                        self.env.pos.db.order_by_id = {};

                                        if (orders) {
                                            if (orders['order']) {
                                                self.env.pos.db.all_orders(orders['order']);
                                            }
                                            if (orders['order_line']) {
                                                self.env.pos.db.all_orders_line(orders['order_line']);
                                            }
                                        }
                                        self.all_order = self.env.pos.db.all_order;

                                        self.render()
                                    }).catch(function (reason) {
                                        var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(pageNumber) - 1)
                                        var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page)
                                        self.env.pos.db.all_order = self.env.pos.db.all_non_return_order.slice(showFrom, showTo)
                                        self.env.pos.db.all_display_order = self.env.pos.db.all_order;
                                        self.all_order = self.env.pos.db.all_order;
                                        self.render()
                                    });

                                } else {
                                    rpc.query({
                                        model: "pos.order",
                                        method: "search_return_exchange_order",
                                        args: [self.env.pos.config, pageNumber + 1]
                                    }).then(function (orders) {
                                        if (orders) {
                                            if (orders['order'].length == 0) {
                                                $($('.next').parent()).addClass('disabled')
                                                $(".next").replaceWith(function () {
                                                    $("<span class='current next'>Next</span>");
                                                });
                                            }
                                        }
                                    }).catch(function (reason) {

                                        var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(pageNumber + 1) - 1)
                                        var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page)
                                        var order = self.env.pos.db.all_return_order.slice(showFrom, showTo)
                                        if (order && order.length == 0) {
                                            $($('.next').parent()).addClass('disabled')
                                            $(".next").replaceWith(function () {
                                                $("<span class='current next'>Next</span>");
                                            });
                                        }

                                    });

                                    rpc.query({
                                        model: "pos.order",
                                        method: "search_return_exchange_order",
                                        args: [self.env.pos.config, pageNumber]
                                    }).then(function (orders) {
                                        self.env.pos.db.all_order = [];
                                        self.env.pos.db.order_by_id = {};

                                        if (orders) {
                                            if (orders['order']) {
                                                self.env.pos.db.all_orders(orders['order']);
                                            }
                                            if (orders['order_line']) {
                                                self.env.pos.db.all_orders_line(orders['order_line']);
                                            }
                                        }
                                        self.all_order = self.env.pos.db.all_order;
                                        self.env.pos.db.all_display_order = self.env.pos.db.all_order;
                                        self.render()
                                    }).catch(function (reason) {

                                        var showFrom = parseInt(self.env.pos.config.sh_how_many_order_per_page) * (parseInt(pageNumber) - 1)
                                        var showTo = showFrom + parseInt(self.env.pos.config.sh_how_many_order_per_page)
                                        self.env.pos.db.all_order = self.env.pos.db.all_return_order.slice(showFrom, showTo)
                                        self.all_order = self.env.pos.db.all_order;
                                        self.render()

                                    });
                                }

                            } catch (error) {
                            }

                        }
                    });
                }
                super.mounted()
                if (self.env.pos.get_order().is_client_order_filter) {
                    $('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.customer_order_length / self.env.pos.config.sh_how_many_order_per_page));

                } else {
                    if (!self.return_filter) {
                        $('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.db.all_non_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                    } else {
                        $('.sh_pagination').pagination('updateItems', Math.ceil(self.env.pos.db.all_return_order.length / self.env.pos.config.sh_how_many_order_per_page));
                    }
                }
                $('.sh_pagination').pagination('selectPage', 1);
            }
        };
    Registries.Component.extend(OrderListScreen, PosOrderListScreen);

    const PosReturnPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
            }
            cancel_return_order() {
                var self = this;

                if (this.env.pos.get_order() && this.env.pos.get_order().get_orderlines() && this.env.pos.get_order().get_orderlines().length > 0) {
                    var orderlines = this.env.pos.get_order().get_orderlines();
                    _.each(orderlines, function (each_orderline) {
                        if (self.env.pos.get_order().get_orderlines()[0]) {
                            self.env.pos.get_order().remove_orderline(self.env.pos.get_order().get_orderlines()[0]);
                        }
                    });
                }
                self.env.pos.get_order().is_return_order(false);
                self.env.pos.get_order().return_order = false;
                self.env.pos.get_order().is_exchange_order(false);
                self.env.pos.get_order().exchange_order = false;
                self.env.pos.get_order().set_old_pos_reference(false);
                self.showScreen("ProductScreen");
            }
            async _finalizeValidation() {
                if (this.currentOrder.is_paid_with_cash() && this.env.pos.config.iface_cashdrawer) {
                    this.env.pos.proxy.printer.open_cashbox();
                }

                this.currentOrder.initialize_validation_date();
                this.currentOrder.finalized = true;

                let syncedOrderBackendIds = [];

                try {
                    if (this.currentOrder.is_to_invoice()) {
                        syncedOrderBackendIds = await this.env.pos.push_and_invoice_order(this.currentOrder);
                    } else {
                        syncedOrderBackendIds = await this.env.pos.push_single_order(this.currentOrder);
                    }
                } catch (error) {
                    if (error instanceof Error) {
                        throw error;
                    } else {
                        await this._handlePushOrderError(error);
                    }
                }
                if (syncedOrderBackendIds.length && this.currentOrder.wait_for_push_order()) {
                    const result = await this._postPushOrderResolve(this.currentOrder, syncedOrderBackendIds);
                    if (!result) {
                        await this.showPopup("ErrorPopup", {
                            title: "Error: no internet connection.",
                            body: error,
                        });
                    }
                }
                if (this.currentOrder.return_order) {
                    this.currentOrder.is_return_order(true);
                    if (this.currentOrder.old_pos_reference) {
                        this.currentOrder.set_old_pos_reference(this.currentOrder.old_pos_reference);
                        this.currentOrder.set_old_sh_uid(this.currentOrder.old_sh_uid);

                        var order = this.currentOrder.export_as_JSON()
                        if (order["amount_paid"] >= parseInt(order["amount_total"])) {
                            order["state"] = "paid";
                        } else {
                            order["state"] = "draft";
                        }
                        order["date_order"] = this.env.pos.formatted_validation_date;
                        order["pos_reference"] = order.name;
                        this.env.pos.db.all_return_order.push(order)
                    }
                } else if (this.currentOrder.exchange_order) {
                    this.currentOrder.is_exchange_order(true);
                    if (this.currentOrder.old_pos_reference) {
                        this.currentOrder.set_old_pos_reference(this.currentOrder.old_pos_reference);
                        this.currentOrder.set_old_sh_uid(this.currentOrder.old_sh_uid);

                        var order = this.currentOrder.export_as_JSON()
                        if (order["amount_paid"] >= parseInt(order["amount_total"])) {
                            order["state"] = "paid";
                        } else {
                            order["state"] = "draft";
                        }
                        order["date_order"] = this.env.pos.formatted_validation_date;
                        order["pos_reference"] = order.name;
                        this.env.pos.db.all_return_order.push(order)
                    }
                } else {
                    var order = this.currentOrder.export_as_JSON()
                    //                	order['pos_reference'] = order['name']

                    if (order["amount_paid"] >= parseInt(order["amount_total"])) {
                        order["state"] = "paid";
                    } else {
                        order["state"] = "draft";
                    }
                    order["date_order"] = this.env.pos.formatted_validation_date;
                    order["pos_reference"] = order.name;

                    this.env.pos.db.all_non_return_order.push(order)
                }
                this.showScreen(this.nextScreen);

                // If we succeeded in syncing the current order, and
                // there are still other orders that are left unsynced,
                // we ask the user if he is willing to wait and sync them.
                if (syncedOrderBackendIds.length && this.env.pos.db.get_orders().length) {
                    const { confirmed } = await this.showPopup("ConfirmPopup", {
                        title: this.env._t("Remaining unsynced orders"),
                        body: this.env._t("There are unsynced orders. Do you want to sync these orders?"),
                    });
                    if (confirmed) {
                        // NOTE: Not yet sure if this should be awaited or not.
                        // If awaited, some operations like changing screen
                        // might not work.
                        this.env.pos.push_orders();
                    }
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PosReturnPaymentScreen);

    // return { OrderListScreen, PosReturnPaymentScreen };
    return { PosReturnPaymentScreen }
});
