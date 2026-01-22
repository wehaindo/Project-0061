odoo.define('pos_cash_opening_zero.CashInOutReceipt', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    const { onWillUpdateProps } = owl;

    class CashInOutReceipt extends PosComponent {
        setup() {
            super.setup();
            this.receiptData = this.props.receiptData;
        }


        get header(){
            if (this.type === "in"){
                return "* * LOAN * *";
            }if (this.type === "out") {
                return "* * PICKUP * *";
            } else {
                return "* * CASH COUNT 1 * *";
            }  
        }

        get storeName(){
            return this.env.pos.config.branch_code;
        }

        get type(){
            return this.receiptData.type;
        }

        get amount(){
            return this.env.pos.format_currency(this.receiptData.amount).replace(',', '.');
        }

        get reason(){
            return this.receiptData.reason;
        }

        get details(){
            //Looping Details 
            return this.receiptData.details.map(detail => {
                return {
                    product: detail.description,
                    quantity: detail.quantity,
                    price: this.env.pos.format_currency(detail.total).replace(',', '.'),
                };
            });
        }

        get dateTrans(){
            return this.receiptData.date;
        }

        get supervisor(){
            return this.receiptData.supervisor.name.substring(0, 9);
        }

        get cashier(){
            return this.receiptData.cashier.name.substring(0, 9);
        }
    }


    CashInOutReceipt.template = 'CashInOutReceipt';

    Registries.Component.add(CashInOutReceipt);

    return CashInOutReceipt;


});