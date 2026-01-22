
odoo.define('weha_pos_foodcourt.eWalletButton', function(require){
    const { eWalletButton } = require('@pos_loyalty/js/ControlButtons/eWalletButton');
    const Registries = require("point_of_sale.Registries");
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    
    const PosFoodcourtEWalletButton = (eWalletButton) => 
        class extends eWalletButton {
            async _onClickWalletButton() {
                console.log("Override _onClickWalletButton");
                const order = this.env.pos.get_order();
                const eWalletPrograms = this.env.pos.programs.filter((p) => p.program_type == 'ewallet');
                const orderTotal = order.get_total_with_tax();
                const eWalletRewards = this._getEWalletRewards(order);
                if (orderTotal < 0 && eWalletPrograms.length >= 1) {
                    console.log('eWalletPrograms');
                    let selectedProgram = null;
                    if (eWalletPrograms.length == 1) {
                        console.log('Only 1 eWalletProgram');
                        selectedProgram = eWalletPrograms[0];
                    } else {
                        console.log('More than 1 eWalletProgram');
                        const { confirmed, payload } = await this.showPopup('SelectionPopup', {
                            title: this.env._t('Refund with eWallet'),
                            list: eWalletPrograms.map((program) => ({
                                id: program.id,
                                item: program,
                                label: program.name,
                            })),
                        });
                        if (confirmed) {
                            selectedProgram = payload;
                        }
                    }
                    if (selectedProgram) {
                        console.log('Process Selected Program');
                        const eWalletProduct = this.env.pos.db.get_product_by_id(selectedProgram.trigger_product_ids[0]);
                        let { confirmed, payload: code } = await this.showPopup('TextInputPopup', {
                            title: this.env._t('Scan Customer Card'),
                            startingValue: '',
                            placeholder: this.env._t('Tap or Scan Customer Card'),
                        });
                        if (confirmed) {
                            // code = code.trim();
                            // if (code !== '') {
                            //     this.env.pos.get_order().activateCode(code);
                            // }
                            order.add_product(eWalletProduct, {
                                price: -orderTotal,
                                merge: false,
                                eWalletGiftCardProgram: selectedProgram,
                            });
                        }
                    }
                } else if (eWalletRewards.length >= 1) {
                    console.log('eWalletRewards');
                    let eWalletReward = null;
                    if (eWalletRewards.length == 1) {
                        eWalletReward = eWalletRewards[0];
                    } else {
                        const { confirmed, payload } = await this.showPopup('SelectionPopup', {
                            title: this.env._t('Use eWallet to pay'),
                            list: eWalletRewards.map(({ reward, coupon_id }) => ({
                                id: reward.id,
                                item: { reward, coupon_id },
                                label: `${reward.description} (${reward.program_id.name})`,
                            })),
                        });
                        if (confirmed) {
                            eWalletReward = payload;
                        }
                    }
                    if (eWalletReward) {
                        let { confirmed, payload: code } = await this.showPopup('TextInputPopup', {
                            title: this.env._t('Scan Customer Card'),
                            startingValue: '',
                            placeholder: this.env._t('Tap or Scan Customer Card'),
                        });
                        if (confirmed) {
                            const result = order._applyReward(eWalletReward.reward, eWalletReward.coupon_id, {});
                            if (result !== true) {
                                // Returned an error
                                this.showPopup('ErrorPopup', {
                                    title: this.env._t('Error'),
                                    body: result,
                                });
                            }
                            order._updateRewards();
                            this.showScreen('PaymentScreen');
                        }
                        
                    }
                }
            }
        };
    
    Registries.Component.extend(eWalletButton, PosFoodcourtEWalletButton);

    return eWalletButton;

});



// import { eWalletButton } from '@pos_loyalty/js/ControlButtons/eWalletButton';
