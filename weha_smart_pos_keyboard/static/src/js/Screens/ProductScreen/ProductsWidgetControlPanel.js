
/** @odoo-module **/

import ProductsWidgetControlPanel from 'point_of_sale.ProductsWidgetControlPanel';
import Registries from 'point_of_sale.Registries';
import { onMounted } from "@odoo/owl";
// import KioskBoard from 'kioskboard';

export const KeyboardProductProductsWidgetControlPanel = (ProductsWidgetControlPanel) => 
    class extends ProductsWidgetControlPanel {
        setup() {
            super.setup();
            console.log("Setup for Module Keyboard Product Screen");
            onMounted(() => this._mounted());
        }            

        _mounted() {
            console.log('KioskBord Mounted');
            // KioskBoard.init({
            //     keysArrayOfObjects: null,
            //     keysJsonUrl: '/weha_smart_pos_keyboard/static/src/libs/kioskboard-keys-english.json',
            //     keysSpecialCharsArrayOfStrings: null,
            //     keysNumpadArrayOfNumbers: null,
            //     language: 'en',
            //     theme: 'light',              
            // });
            var turkishKeyboard = [
                {
                  "0": "Q",
                  "1": "W",
                  "2": "E",
                  "3": "R",
                  "4": "T",
                  "5": "Y",
                  "6": "U",
                  "7": "I",
                  "8": "O",
                  "9": "P",
                  "10": "Ğ",
                  "11": "Ü"
                },
                {
                  "0": "A",
                  "1": "S",
                  "2": "D",
                  "3": "F",
                  "4": "G",
                  "5": "H",
                  "6": "J",
                  "7": "K",
                  "8": "L",
                  "9": "Ş",
                  "10": "İ",
                },
                {
                  "0": "Z",
                  "1": "X",
                  "2": "C",
                  "3": "V",
                  "4": "B",
                  "5": "N",
                  "6": "M",
                  "7": "Ö",
                  "8": "Ç",
                }
              ];
            KioskBoard.run('.js-kioskboard-input', {
                keysArrayOfObjects: turkishKeyboard,
                // keysNumpadArrayOfNumbers: [1, 2, 3, 4, 5, 6, 7, 8, 9, 0],
                // keysSpecialCharsArrayOfStrings: ['a', 'b', 'c'],
                // keysJsonUrl: 'kioskboard-keys-turkish.json',
                language: 'tr',
                keysFontFamily: 'Barlow',
                keysFontWeight: '500',
                cssAnimationsStyle: 'fade',
                theme: 'dark',
                // keysFontSize: '20px',
                allowRealKeyboard: true,
                allowMobileKeyboard: true,
                // keysAllowSpacebar: false,
              });
            KioskBoard.run('.js-kioskboard-input'); 
            
        }

    };
        
Registries.Component.extend(ProductsWidgetControlPanel, KeyboardProductProductsWidgetControlPanel)
