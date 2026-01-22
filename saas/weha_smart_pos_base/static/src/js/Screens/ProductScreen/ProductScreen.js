odoo.define('weha_smart_pos_base.ProductScreen', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen');
	const { onMounted } = owl;

	const BaseProductScreen= (ProductScreen) =>
		class extends ProductScreen {
			setup() {
				super.setup();
				var self = this;
				onMounted(() => this._mounted());
			}

			_mounted() {
                console.log('Mounted Send Message');
				let self = this;                
                this.env.services['bus_service'].addEventListener('notification', ({ detail: notifications }) => {
                    console.log('Received Message');
                    self.showMessage(notifications);
                });			
			}

            showMessage(notifications){
                console.log('Notification Message');
                let self = this;
                notifications.forEach(function (ntf) {
                    ntf = JSON.parse(JSON.stringify(ntf));
                    console.log(ntf);
                    if(ntf && ntf.type && ntf.type == "pos.session/send_message"){
                        if (ntf.payload.config_id == self.env.pos.config.id){
                            console.log(ntf.payload);
                            self.showPopup('SendMessagePopup',{'message': ntf.payload.message});
                        }
                    }
                })                  
            }
			
		};

	Registries.Component.extend(ProductScreen, BaseProductScreen);

	return ProductScreen;

});

    