odoo.define('weha_smart_pos_aeon_price_change.PriceOverrideButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class PriceOverrideButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }

        get get_selected_orderline() {
            return this.env.pos.get_order().get_selected_orderline();            
        }

        async onClick() {
            var self = this;
            var orderline =  this.env.pos.get_order().get_selected_orderline();
            if (orderline) {           
     
                var overridereasons = [
                    {id: '001', description: 'P-System not update'},
                    {id: '002', description: 'P-Price Card not update'},
                    {id: '003', description: 'P-Expire POP'},
                    {id: '004', description: 'P-Wrong POP'},
                    {id: '005', description: 'P-Seito/Price checker issue'},
                    {id: '006', description: 'Scanning'},
                    {id: '007', description: 'Wrong Purchase'},
                    {id: '008', description: 'Expired'},
                    {id: '009', description: 'Damage'},
                    {id: '010', description: 'Discount'},
                    {id: '011', description: 'Cancel Item'},
                    {id: '012', description: 'Exchange'},
                    {id: '013', description: 'Payment'},
                    {id: '014', description: 'VAT'},
                    {id: '015', description: 'Others'},                    
                ]

                const selectionList = overridereasons.map(overridereason => ({
                    id: overridereason.id,
                    label: overridereason.description,
                    isSelected: false,
                    item: overridereason,
                }));     

                const { confirmed, payload: selectedReason } = await this.showPopup(
                    'SelectionPopup',
                    {
                        title: this.env._t('Select the Price Override Reason'),
                        list: selectionList,
                    }
                );

                // const { confirmed, payload} = await this.showPopup('TextInputPopup', {
                //     title: 'Price Override Reason Code',
                //     isInputSelected: true,
                // });                
                if(confirmed){
                    var reasonCode = selectedReason.id;
                    const { confirmed, payload } = await this.showPopup('NumberDenomPopup', {
                        title: this.env._t('Input New Price'),
                        isInputSelected: true,
                    });    
                    var newPrice = payload;
                    if ( confirmed ) {
                        // Show supervisor grid first
                        const employees = this.env.pos.res_users_supervisors
                        .filter((supervisor) => this.env.pos.employee_by_user_id[supervisor.id])
                        .map((supervisor) => {
                            const employee = this.env.pos.employee_by_user_id[supervisor.id]
                            return {
                                id: employee.id,
                                item: employee,
                                label: employee.name,
                                isSelected: false,
                                fingerprintPrimary: employee.fingerprint_primary,
                            };
                        });

                        let {confirmed: supervisorConfirmed, payload: employee} = await this.showPopup('SupervisorGridPopup', {
                            title: this.env._t('Supervisor'),
                            employees: employees,
                        });

                        if (supervisorConfirmed && employee) {
                            // Check if supervisor is the same as current user
                            if(employee.user_id && employee.user_id[0] === this.env.pos.config.current_user_id[0]){
                                await this.showPopup('ErrorPopup', {
                                    body: this.env._t('Supervisor cannot override product price!'),                    
                                });
                                return;
                            }

                            // Ask for PIN after selecting supervisor
                            if (employee.pin) {
                                const { confirmed, payload: inputPin } = await this.showPopup('NumberPopup', {
                                    isPassword: true,
                                    title: this.env._t('Password ?'),
                                    startingValue: null,
                                });

                                if (confirmed && employee.pin === inputPin) {
                                    console.log('supervisor');
                                    console.log(employee);
                                    orderline.price_manually_set = true;
                                    orderline.set_unit_price(newPrice);
                                    orderline.set_price_source('override');    
                                    orderline.set_price_override_user(employee.user_id[0]);
                                    orderline.set_price_override_reason(reasonCode);
                                } else {
                                    await this.showPopup('ErrorPopup', {
                                        body: this.env._t('Incorrect Password'),                    
                                    });
                                }
                            } else {
                                console.log('supervisor');
                                console.log(employee);
                                orderline.price_manually_set = true;
                                orderline.set_unit_price(newPrice);
                                orderline.set_price_source('override');    
                                orderline.set_price_override_user(employee.user_id[0]);
                                orderline.set_price_override_reason(reasonCode);
                            }
                        } else {
                            await this.showPopup('ErrorPopup', {
                                body: this.env._t('Price override failed!'),                    
                            });
                        }
                    }
    
                }
            }
        }
    }
    
    PriceOverrideButton.template = 'PriceOverrideButton';

    ProductScreen.addControlButton({
        component: PriceOverrideButton,
        condition: function() {
            return this.env.pos.config.allow_price_override
        },
    });

    Registries.Component.add(PriceOverrideButton);

    return PriceOverrideButton;
});