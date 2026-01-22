odoo.define('bi_pos_reports.XMLPosOrderSummaryReceipt', function(require) {
	'use strict';

	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');

	class XMLPosOrderSummaryReceipt extends PosComponent {
		setup() {
			super.setup();
		}
		get summery(){
			let categs = this.props.order;
			let summery = [];
			$.each(categs, function( i, categs ){
				if(categs){
					summery.push(categs)
				}
			});
			console.log("summery----------",summery)
			return summery;
		}
	}
	
	XMLPosOrderSummaryReceipt.template = 'XMLPosOrderSummaryReceipt';
	Registries.Component.add(XMLPosOrderSummaryReceipt);
	return XMLPosOrderSummaryReceipt;
});
