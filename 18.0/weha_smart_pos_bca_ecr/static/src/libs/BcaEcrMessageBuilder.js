export class BcaEcrMessageBuilder {
    constructor() {}

    // 🔹 Helpers
    pad(val, len, char = '0') {
        return String(val).padStart(len, char);
    }

    padRight(val, len, char = ' ') {
        return String(val).padEnd(len, char);
    }
    
    hex_to_ascii(hex_data){
        var hex  = hex_data.toString();
        var str = '';
        for (var n = 0; n < hex.length; n += 2) {
            str += String.fromCharCode(parseInt(hex.substr(n, 2), 16));
        }
        return str;
    }

    // getAmountPart(amount) {
    //     return Math.floor(amount).toString();
    // }


    getAmountPart(num) {       
          const amountStr = num.toString().split('.')[0];
          return amountStr;
    }

    // getDecimalPart(amount) {
    //     return this.pad(Math.round((amount % 1) * 100), 2);
    // }

    getDecimalPart(num) {
          if (Number.isInteger(num)) {
            return "00";
          }        
          const decimalStr = num.toString().split('.')[1];
          if(parseInt(decimalStr) === 0){
            return "00"
          }
          if(decimalStr.length === 1){
            return decimalStr + "0";
          }
          return decimalStr;
    }

    calculateLRC(bytes) {
        return bytes.reduce((acc, b) => acc ^ b, 0);
    }

    _getArrInt(str){
        console.log(str);
        var myArray = str.match(/.{2}/g);
        var arrSend = [];
        for (var i = 0, l = myArray.length; i < l; i ++) {
            var hex_str = "0x" + myArray[i];
            var hex_int = parseInt(hex_str, 16);
            var new_int = hex_int + 0x200;
            arrSend.push(new_int);
        }        
        return arrSend;
    }

    // _getBytesForLcr(message_length, ecr_version, data_in_str, end_of_text) {
    //     const msg = message_length + ecr_version + data_in_str + end_of_text;
    //     return [...msg].map(c => c.charCodeAt(0));
    // }

    _getBytesForLcr(message_length, ecr_version, str, end_of_text){
        let int_message_length = this._getArrInt(message_length);
        let int_ecr_version = this._getArrInt(ecr_version);
        let int_end_of_text = this._getArrInt(end_of_text);
        let intArray=str.split ('').map (function (c) { return c.charCodeAt (0); });  
        let concatArray = int_message_length.concat(int_ecr_version,intArray,int_end_of_text)
        let byteArray=new Uint8Array(concatArray.length);
        for (let i=0;i<concatArray.length;i++)
        byteArray[i]=concatArray[i];
        return byteArray;
    }

    // _getBytesForMessage(start_of_text, message_length, ecr_version, data_in_str, end_of_text, lrc) {
    //     return [
    //         parseInt(start_of_text, 16),
    //         ...[...message_length + ecr_version + data_in_str].map(c => c.charCodeAt(0)),
    //         parseInt(end_of_text, 16),
    //         lrc
    //     ];
    // }
    
    _getBytesForMessage(start_of_text, message_length, ecr_version, str, end_of_text, lcr){
          let int_start_of_text = this._getArrInt(start_of_text);
          let int_message_length = this._getArrInt(message_length);
          let int_ecr_version = this._getArrInt(ecr_version);
          let int_end_of_text = this._getArrInt(end_of_text);    
          
          let intArray=str.split ('').map (function (c) { return c.charCodeAt (0); });    
          let concatArray = int_start_of_text.concat(int_message_length,int_ecr_version,intArray,int_end_of_text,lcr);
          console.log(concatArray);
          let byteArray=new Uint8Array(concatArray.length);
          for (let i=0;i<concatArray.length;i++)
            byteArray[i]=concatArray[i];
          return byteArray;
    }

    // 🔹 Main
    // generateEcrMessage(trans_type, paymentLine) {
    //     let pan = this.padRight('', 19, ' ');
    //     let expirydate = this.padRight('', 4, ' ');

    //     // Transaction amount
    //     const amount = this.getAmountPart(paymentLine.amount);
    //     const decimal_amount = this.getDecimalPart(paymentLine.amount);
    //     const transaction_amount = this.pad(amount, 10) + decimal_amount;

    //     let data = {
    //         start_of_text: '02',
    //         message_length: '0150',
    //         ecr_version: '02',
    //         transaction_type: trans_type,
    //         transaction_amount,
    //         other_amount: '000000000000',
    //         pan,
    //         expireddate: expirydate,
    //         cancel_reason: '00',
    //         invoice_reason: '000000',
    //         auth_code: this.padRight('', 6, ' '),
    //         installment_flag: ' ',
    //         redeem_flag: ' ',
    //         dcc_flag: 'N',
    //         installment_plan: this.padRight('', 3, ' '),
    //         installment_tenor: this.padRight('', 2, ' '),
    //         generic_data: this.padRight('', 12, ' '),
    //         refference_number: '000000000000',
    //         original_date: this.padRight('', 4, ' '),
    //         bca_filler: this.padRight('', 50, ' '),
    //         end_of_text: '03'
    //     };

    //     // Special case: Void (32)
    //     if (trans_type === '32') {
    //         data.ecr_version = '03';
    //         data.transaction_amount = '000000000000';
    //         data.refference_number = this.pad(paymentLine.reff_number, 12);
    //     }

    //     // Build concatenated string
    //     const data_in_str =
    //         data.transaction_type +
    //         data.transaction_amount +
    //         data.other_amount +
    //         data.pan +
    //         data.expireddate +
    //         data.cancel_reason +
    //         data.invoice_reason +
    //         data.auth_code +
    //         data.installment_flag +
    //         data.redeem_flag +
    //         data.dcc_flag +
    //         data.installment_plan +
    //         data.installment_tenor +
    //         data.generic_data +
    //         data.refference_number +
    //         data.original_date +
    //         data.bca_filler;

    //     // Recalculate length
    //     data.message_length = this.pad(data_in_str.length + 3, 4);

    //     // LRC
    //     const data_for_lcr = this._getBytesForLcr(
    //         data.message_length, data.ecr_version, data_in_str, data.end_of_text
    //     );
    //     const lrc = this.calculateLRC(data_for_lcr);

    //     const data_in_hex = this._getBytesForMessage(
    //         data.start_of_text, data.message_length, data.ecr_version, data_in_str, data.end_of_text, lrc
    //     );

    //     return {
    //         type: 'bca_ecr',
    //         name: 'Payment BCA ECR',
    //         // value: data_in_hex.join(),
    //         // hex_dump: data_in_hex.map(b => b.toString(16).padStart(2, '0')).join(' ')
    //         value: data_in_hex.map(b => b.toString(16).padStart(2, '0')).join('').replace(",", "")
    //     };
    // }

    generate_ecr_message(trans_type, paymentLine){
        console.log('Generate ECR Message');
        var pan = '                   ';
        var expirydate = '    ';
        // if(paymentLine.payment_method.is_dev){            
        //     pan  = paymentLine.payment_method.pan + '   ';
        //     expirydate = paymentLine.payment_method.expirydate;
        // }
        console.log("paymentline.amount");
        console.log(paymentLine.amount);
        var amount = this.getAmountPart(paymentLine.amount)
        console.log("amount");
        console.log(amount);
        var decimal_amount = this.getDecimalPart(paymentLine.amount);
        console.log("decimal_amount");
        console.log(decimal_amount);
        var transaction_amount = amount.padStart(10,'0') + decimal_amount;
        console.log("transaction_amount");
        console.log(transaction_amount);
        var data = {
        start_of_text: '02', // 1 Digit (HEX)
        message_length: '0150',  // 4 Digit (HEX)
        ecr_version: '02', // (HEX)
        // transaction_type: paymentLine.payment_method.trans_type, // (ASCII) 2 Digit
        transaction_type: trans_type,
        // transaction_amount: '000000010000', // (ASCII) 12 Digit
        transaction_amount: transaction_amount,
        other_amount: '000000000000', // (ASCII) 12 Digit
        //pan: '5409120012345684   ', // (ASCII) 19 Digit
        //expire_date: '2510', // (ASCII) 4 Digit
        pan: pan, // (ASCII) 19 Digit
        expireddate: expirydate, // (ASCII) 4 Digit
        cancel_reason: '00', // (ASCII) 2 Digit
        invoice_reason: '000000', // (ASCII) 6 Digit
        auth_code: '      ', // (ASCII) 6 Digit
        installment_flag: ' ', // (ASCII) 1 Digit
        redeem_flag: ' ', // (ASCII) 1 Digit
        dcc_flag: 'N', // (ASCII) 1 Digit
        installment_plan: '   ', // (ASCII) 3 Digit
        installment_tenor: '  ', // (ASCII) 2 Digit
        generic_data: '            ', // (ASCII) 12 Digit
        refference_number: '000000000000', // (ASCII)  12 Digit
        original_date: '    ', // ASCII 4 Digit
        bca_filler: '                                                  ', // (ASCII) 50 Digit
        end_of_text: '03', // (HEX)
        }
        
        if(trans_type == '01' || trans_type == '31'){
            data.trans_type = trans_type;  
        }else if(trans_type == '32'){
        var data = {
            start_of_text: '02', // 1 Digit (HEX)
            message_length: '0150',  // 4 Digit (HEX)
            ecr_version: '03', // (HEX)
            transaction_type: trans_type, // (ASCII) 2 Digit
            transaction_amount: '000000000000', // (ASCII) 12 Digit
            other_amount: '000000000000', // (ASCII) 12 Digit
            pan: '                   ', // (ASCII) 19 Digit
            expireddate: '    ', // (ASCII) 4 Digit
            cancel_reason: '00', // (ASCII) 2 Digit
            invoice_reason: '000000', // (ASCII) 6 Digit
            auth_code: '      ', // (ASCII) 6 Digit
            installment_flag: ' ', // (ASCII) 1 Digit
            redeem_flag: ' ', // (ASCII) 1 Digit
            dcc_flag: 'N', // (ASCII) 1 Digit
            installment_plan: '   ', // (ASCII) 3 Digit
            installment_tenor: '  ', // (ASCII) 2 Digit
            generic_data: '            ', // (ASCII) 12 Digit
            refference_number: paymentLine.get_reff_number(), // (ASCII)  12 Digit
            original_date: '    ', // ASCII 4 Digit
            bca_filler: '                                                  ', // (ASCII) 50 Digit
            end_of_text: '03', // (HEX)        
        }
        // data.refference_number = paymentLine.get_reff_number();
        console.log("Get Reff Number");
        console.log(paymentLine.get_reff_number());
        }

        const data_in_str =                    
        data.transaction_type + 
        data.transaction_amount +  
        data.other_amount + 
        data.pan + 
        data.expireddate + 
        data.cancel_reason + 
        data.invoice_reason + 
        data.auth_code +
        data.installment_flag + 
        data.redeem_flag + 
        data.dcc_flag + 
        data.installment_plan + 
        data.installment_tenor +
        data.generic_data + 
        data.refference_number + 
        data.original_date + 
        data.bca_filler
        
        console.log("data_in_str");
        console.log(data_in_str);

        const data_for_lcr = this._getBytesForLcr(data.message_length, data.ecr_version, data_in_str, data.end_of_text);
        for (let i = 0; i < data_for_lcr.length; i++) {
            if (i == 0 ){
                var var1 = data_for_lcr[i];
            }else{
                var var1 = var1 ^ data_for_lcr[i];            
            }
        }

        const data_in_hex = this._getBytesForMessage(data.start_of_text, data.message_length, data.ecr_version, data_in_str, data.end_of_text, var1);
        var send_message = String
        var type = 'bca_ecr';          
        // console.log("Is Ether : " + paymentLine.payment_method.is_ether);
        // if (paymentLine.payment_method.is_ether === true){
        //     type = 'bca_ecr_ether';          
        // }          
        var message = {
            type: type,
            name: 'Payment BCA ECR',
            value: data_in_hex.join()
        };

        return message;
    }
}
