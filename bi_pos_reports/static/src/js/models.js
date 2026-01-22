/*odoo.define('bi_pos_reports.pos', function(require) {
	"use strict";
	const models = require('point_of_sale.models');
	const screens = require('point_of_sale.ProductScreen');
	const PaymentScreen = require('point_of_sale.PaymentScreenNumpad');
	const ActionpadWidget = require('point_of_sale.ActionpadWidget'); 
	const core = require('web.core');
	const gui = require('point_of_sale.Gui');
	const popups = require('point_of_sale.ConfirmPopup');
	const rpc = require('web.rpc');
	const Registries = require('point_of_sale.Registries');

	var QWeb = core.qweb;
	var _t = core._t;

	models.load_models({	
		model: 'stock.location',
		fields: [],
		domain: function(self) {return [['company_id', '=', self.config.company_id[0]]]},
		loaded: function(self, locations){
			self.locations = locations;
		},
	});

	models.load_models({
		model:  'pos.session',
		domain: null,
		loaded: function(self,pos_sessions){
			self.pos_sessions = pos_sessions
			},
		});

				
	
});
*/

odoo.define('bi_pos_reports.pos', function(require) {
	"use strict";
	var core = require('web.core');
	var utils = require('web.utils');
	var round_pr = utils.round_precision;
	var field_utils = require('web.field_utils');
	const Registries = require('point_of_sale.Registries');
	var { Order, Orderline, PosGlobalState} = require('point_of_sale.models');
	var round_di = utils.round_decimals;



	const BiPOSReports = (PosGlobalState) => class BiPOSReports extends PosGlobalState {

		async _processData(loadedData) {
			await super._processData(...arguments);
			this.pos_sessions = loadedData['pos_sessions'];
			this.locations = loadedData['stock.location'] || [];
			console.log("loadedData--------------",loadedData)
		}
	}

	Registries.Model.extend(PosGlobalState, BiPOSReports);

				
	
});
