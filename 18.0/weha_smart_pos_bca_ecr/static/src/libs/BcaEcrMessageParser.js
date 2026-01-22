export class BcaEcrMessageParser {
    constructor() {
        this.responseCodeMap = {
            "00": "Approved",
            "05": "Do Not Honor",
            "12": "Invalid Transaction",
            "13": "Invalid Amount",
            "14": "Invalid Card Number",
            "30": "Format Error",
            "41": "Lost Card - Pickup",
            "43": "Stolen Card - Pickup",
            "51": "Insufficient Funds",
            "54": "Expired Card",
            "55": "Incorrect PIN",
            "57": "Transaction Not Permitted",
            "58": "Transaction Not Allowed",
            "91": "Issuer or Switch Inoperative",
            "96": "System Malfunction"
        };
    }

    // calculateLRC(bytes) {
    //     return bytes.reduce((acc, b) => acc ^ b, 0);
    // }

    // parseMessage(rawBytes) {
    //     if (rawBytes[0] !== 0x02) throw new Error("Invalid STX");
    //     if (rawBytes[rawBytes.length - 2] !== 0x03) throw new Error("Invalid ETX");

    //     const received_lrc = rawBytes[rawBytes.length - 1];
    //     const asciiBytes = rawBytes.slice(1, -2);
    //     const asciiStr = String.fromCharCode(...asciiBytes);

    //     const message_length = asciiStr.slice(0, 4);
    //     const ecr_version = asciiStr.slice(4, 6);
    //     const data_in_str = asciiStr.slice(6);

    //     const for_lcr = [...asciiBytes, rawBytes[rawBytes.length - 2]];
    //     const calc_lrc = this.calculateLRC(for_lcr);
    //     if (calc_lrc !== received_lrc) {
    //         throw new Error(`LRC mismatch (calc=${calc_lrc}, recv=${received_lrc})`);
    //     }

    //     const parsed = {
    //         message_length,
    //         ecr_version,
    //         transaction_type: data_in_str.slice(0, 2),
    //         transaction_amount: data_in_str.slice(2, 14),
    //         other_amount: data_in_str.slice(14, 26),
    //         pan: data_in_str.slice(26, 45).trim(),
    //         expiry_date: data_in_str.slice(45, 49).trim(),
    //         cancel_reason: data_in_str.slice(49, 51),
    //         invoice_reason: data_in_str.slice(51, 57),
    //         auth_code: data_in_str.slice(57, 63).trim(),
    //         installment_flag: data_in_str.slice(63, 64),
    //         redeem_flag: data_in_str.slice(64, 65),
    //         dcc_flag: data_in_str.slice(65, 66),
    //         installment_plan: data_in_str.slice(66, 69).trim(),
    //         installment_tenor: data_in_str.slice(69, 71).trim(),
    //         generic_data: data_in_str.slice(71, 83).trim(),
    //         reference_number: data_in_str.slice(83, 95).trim(),
    //         original_date: data_in_str.slice(95, 99).trim(),
    //         bca_filler: data_in_str.slice(99, 149).trim()
    //     };

    //     // Map status
    //     const resp_code = parsed.cancel_reason;
    //     parsed.response_code = resp_code;
    //     parsed.status_message = this.responseCodeMap[resp_code] || "Unknown Response Code";

    //     return parsed;
    // }


    parsing_ecr_response(data){
        var jsonData = JSON.parse(data);
        console.log(jsonData);
        var resp_code = jsonData.value.slice(106,110);
        var trans_type = jsonData.value.slice(8,12);
        if (trans_type == "3031"){
        var parsing_data = {
            length: jsonData.value.slice(0,8), // 4
            trans_type: jsonData.value.slice(8,12), // 2
            trans_amount: jsonData.value.slice(12,36), // 12
            other_amount: jsonData.value.slice(36,60), // 12
            pan: jsonData.value.slice(60,98), // 19
            expiry_date: jsonData.value.slice(98,106), // 4
            resp_code: jsonData.value.slice(106,110), // 2
            rrn: jsonData.value.slice(110,134), // 12
            approval_code: jsonData.value.slice(134,146), // 6
            date: jsonData.value.slice(146,162), // 8
            time: jsonData.value.slice(162,174), // 6
            marchant_id: jsonData.value.slice(174,204), // 15
            terminal_id: jsonData.value.slice(204,220), // 8
            offline_flag: jsonData.value.slice(220,222), // 1
            card_holder_name: jsonData.value.slice(222,278), // 26
            pan_cashier_card: jsonData.value.slice(278,310), // 16
            invoice_number: jsonData.value.slice(310,322), // 6
            filler: jsonData.value.slice(322,338) // 8
        };
        }
        
        if (trans_type == "3331" || trans_type == "3332"){
        var parsing_data = {
            length: jsonData.value.slice(0,8), // 4
            trans_type: jsonData.value.slice(8,12), // 2
            trans_amount: jsonData.value.slice(12,36), // 12
            other_amount: jsonData.value.slice(36,60), // 12
            pan: jsonData.value.slice(60,98), // 19 - Benar
            expiry_date: jsonData.value.slice(98,106), // 4 
            resp_code: jsonData.value.slice(106,110), // 2
            rrn: jsonData.value.slice(110,134), // 12
            approval_code: jsonData.value.slice(134,146), // 6
            date: jsonData.value.slice(146,162), // 8  146 + 16 = 162
            time: jsonData.value.slice(162,174), // 6  162 + 12 = 174 
            marchant_id: jsonData.value.slice(180,210), // 15 
            terminal_id: jsonData.value.slice(210,226), // 8
            offline_flag: jsonData.value.slice(226,228), // 1
            card_holder_name: jsonData.value.slice(228,280), // 26 228 + 52
            pan_cashier_card: jsonData.value.slice(278,310), // 16
            invoice_number: jsonData.value.slice(310,322), // 6
            batch_number: jsonData.value.slice(322,334), // 6
            issuer_id: jsonData.value.slice(334,338), // 2
            installment_flag: jsonData.value.slice(338,440), // 1
            ddc_flag: jsonData.value.slice(440,442), // 1
            redeem_flag: jsonData.value.slice(442,444), // 1
            info_amount: jsonData.value.slice(444,468), // 12
            dcc_decimal_place: jsonData.value.slice(468,470), // 1
            ddc_currency_name: jsonData.value.slice(470,476), // 3
            ddc_ex_rate: jsonData.value.slice(476,492), // 8
            coupon_flag: jsonData.value.slice(492,494), // 1
            filler: jsonData.value.slice(494,510) // 8
        };
        }
        console.log("Parsing ECR Response")
        console.log(parsing_data);
        return parsing_data;
    }
}
