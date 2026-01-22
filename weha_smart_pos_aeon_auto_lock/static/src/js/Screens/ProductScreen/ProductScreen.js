odoo.define('weha_smart_pos_aeon_auto_lock.ProductScreen', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen'); 
    const{onMounted,onWillUnmount}=owl;

	const AutoLockProductScreen = (ProductScreen) =>
		class extends ProductScreen {
		constructor() {
			super(...arguments);
            this.inactivityTimer = null;
            this.inactivityLimit = 2 * 60 * 1000; // 5 minutes
            this.locked = false;
            onMounted(() => this.mounted());
            onWillUnmount(() => this.willUnmount());
        }
        
        mounted() {
            this.resetInactivityTimer();
            this._startTrackingUserActivity();
        }
        
        willUnmount() {
            this._stopTrackingUserActivity();
        }
        
        _startTrackingUserActivity() {
            document.addEventListener('mousemove', this._resetTimer.bind(this));
            document.addEventListener('keydown', this._resetTimer.bind(this));
        }

        _stopTrackingUserActivity() {
            document.removeEventListener('mousemove', this._resetTimer.bind(this));
            document.removeEventListener('keydown', this._resetTimer.bind(this));
        }

        _resetTimer() {
            if (this.locked) return;
            clearTimeout(this.inactivityTimer);
            this.inactivityTimer = setTimeout(() => this.showLoginScreen(), this.inactivityLimit);
        }

        _lockPOS() {
            this.locked = true;
            this.showPopup('ConfirmPopup', {
                title: 'Session Locked',
                body: 'Your session has been locked due to inactivity.',
                confirmText: 'Unlock',
                cancelText: 'Logout',
            }).then(result => {
                if (result.confirmed) {
                    this.locked = false;
                    this.resetInactivityTimer();
                } else {
                    // Handle logout if necessary
                }
            });
        }

        async showLoginScreen() {            
            this.env.pos.reset_cashier();
            await this.showTempScreen('LoginScreen');
        }

        resetInactivityTimer() {
            this._resetTimer();
        }
    };
    
    Registries.Component.extend(ProductScreen, AutoLockProductScreen);
    return ProductScreen;
});
