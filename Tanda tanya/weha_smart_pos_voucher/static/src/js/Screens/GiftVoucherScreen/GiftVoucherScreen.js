odoo.define('weha_smart_pos_voucher.GiftVoucherScreen', function(require) {
'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    class GiftVoucherScreen extends PosComponent {
        setup() {
            super.setup();
            useListener('close-screen', this.close);
            useListener('filter-selected', this._onFilterSelected);
            useListener('search', this._onSearch);
            useListener('click-voucher-line', this.clickVoucher);
            this.searchDetails = {};
            this.filter = null;
            this.state = {
                query: null,
                selectedVoucher: this.props.gift_voucher,
                detailIsShown: false,
            }
        }
        close(){
            this.showScreen('ProductScreen');
        }
        _onFilterSelected(event) {
            this.filter = event.detail.filter;
            this.render();
        }
        async clickVoucher(event) {
            if(event != undefined){
                 let Voucher = event.detail;
                 this.state.selectedVoucher = Voucher;
                 await this.rpc({
                    model: 'aspl.gift.voucher.redeem',
                    method: 'search_read',
                    domain: [['voucher_id', '=', this.state.selectedVoucher.id]],
                 }, {async: true}).then((gift_voucher) => {
                    this.history = gift_voucher
                 })
                 this.VoucherHistory = this.history
                 this.render();
            }
        }
        get highlight() {
            return this.state.selectedVoucher !== this.state.selectedVoucher ? '' : 'highlight';
        }
        back() {
            if(this.state.detailIsShown) {
                this.state.detailIsShown = false;
                this.render();
            } else {
                this.trigger('close-screen');
            }
        }
        get GiftVoucherList() {
            return this.env.pos.gift_vouchers;
        }
        _onSearch(event) {
            const searchDetails = event.detail;
            Object.assign(this.searchDetails, searchDetails);
            this.render();
        }
        get filteredGiftVoucherList() {
            const { fieldName, searchTerm } = this.searchDetails;
            const searchField = this._getsearchFields()[fieldName];
            const searchCheck = (order) => {
                if (!searchField) return true;
                const repr = searchField.repr(order);
                if (repr === null) return true;
                if (!searchTerm) return true;
                return repr && repr.toString().toLowerCase().includes(searchTerm.toLowerCase());
            };
            const predicate = (order) => {
                return searchCheck(order);
            };
            return this.GiftVoucherList.filter(predicate);
        }
        getSearchGiftVoucherConfig() {
            return {
                searchFields: new Map(
                    Object.entries(this._getsearchFields()).map(([key, val]) => [key, val.displayName])
                ),
                filter: { show: true, options: this._getFilterOptions() },
                defaultSearchDetails: this.searchDetails,
                defaultFilter: this.filter,
            };
        }
        _getFilterOptions(){
            const orderStates = this._getOrderStates();
            return orderStates;
        }
        _getOrderStates() {
            const states = new Map();
            states.set('VOUCHER', {
                text: this.env._t('Voucher'),
            });
            return states;
        }
        _getsearchFields() {
            var fields = {}
            fields = {
                VOUCHER_NUMBER:{
                    'repr': (order) => order.voucher_code,
                    displayName: this.env._t('Voucher Number'),
                    modelField: 'voucher_code',
                },
                VOUCHER_NAME:{
                    'repr': (order) => order.voucher_name,
                    displayName: this.env._t('Voucher Name'),
                    modelField: 'voucher_name',
                },
                EXPIRE_DATE:{
                    'repr': (order) => moment(order.expiry_date).format('YYYY-MM-DD hh:mm A'),
                    displayName: this.env._t('Expire Date(YYYY-MM-DD hh:mm A)'),
                    modelField: 'expire_date',
                }
            };
            return fields;
        }
    }
    GiftVoucherScreen.template = 'GiftVoucherScreen';

    Registries.Component.add(GiftVoucherScreen);

    return GiftVoucherScreen;
});