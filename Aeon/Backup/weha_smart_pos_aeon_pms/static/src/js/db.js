odoo.define("weha_smart_pos_aeon_pms.db", function(require) {
    "use strict";

    var DB = require("point_of_sale.DB");
    var { Product } = require('point_of_sale.models');
    var rpc = require('web.rpc');

    var save_prototype = DB.prototype.save;

    // var core = require('web.core');
    // var _t = core._t;

    // // Define the RPC function
    // function callRPC(args) {
    //     return new Promise(function (resolve, reject) {
    //         var url = '/web/dataset/call_kw';
    //         var params = {
    //             model: args.model,
    //             method: args.method,
    //             args: args.args || [],
    //             kwargs: args.kwargs || {},
    //         };

    //         // Make the RPC call
    //         core.ajax.jsonRpc(url, 'call', params)
    //             .then(function (result) {
    //                 resolve(result);
    //             })
    //             .catch(function (error) {
    //                 reject(error);
    //             });
    //     });
    // }

    function padTo2Digits(num) {
        return num.toString().padStart(2, '0');
    }
      
    function formatDate(date) {
        return (
          [ 
            padTo2Digits(date.getDate()),           
            padTo2Digits(date.getMonth() + 1),
            date.getFullYear(),
          ].join('-') +
          ' ' +
          [
            padTo2Digits(date.getHours()),
            padTo2Digits(date.getMinutes()),
            padTo2Digits(date.getSeconds()),
          ].join(':')
        );
      }

    // DB.prototype.save = function(store,data){
    //     console.log("SAVE Prototype");
    //     console.log(store);
    //     console.log(data);
    //     save_prototype.apply(this, arguments);
    //     // Update /api/device/Trade to PMS
    //     if(Array.isArray(data)){
    //         console.log('Data Array');
    //         if(store == 'unpaid_orders' || store == 'unpaid_orders_to_remove'){
    //             console.log('Order In Progress')
    //             return
    //         }else{
    //             console.log('Order Sent To Server')
    //             console.log(data);
    //             const values = data.values();
    //             for (let dt of values){
    //                 console.log(dt)                    
    //                 var id = dt.id;
    //                 var order_data = dt.data;         
    //                 console.log("Order Data");
    //                 console.log(order_data);
    //                 if(order_data.is_aeon_member == true){
    //                     var lines = order_data.lines.values();
    //                     var consumption_list = [];                    
    //                     for(let line of lines){
    //                         var line_data = line[2];                        
    //                         console.log(line_data);
    //                         var consumption = {
    //                             "number":line_data.qty,
    //                             "price":line_data.price_unit,
    //                             "product_id": line_data.product_id.toString(),
    //                             "product_name":line_data.full_product_name,
    //                             "remarks":"",
    //                             "total":line_data.price_subtotal
    //                         }
    //                         consumption_list.push(consumption);
    //                     }
    //                     var pay_tools = []
    //                     var statements = order_data.statement_ids.values();
    //                     for(let statement of statements){
    //                         var statement_data = statement[2];                        
    //                         var pay = {
    //                             "pay_amount":statement_data.amount,
    //                             "pay_type":"KWK"
    //                         }
    //                         pay_tools.push(pay);
    //                     }
    //                     var trade_data = {
    //                         "card_no": order_data.card_no,
    //                         "pos_code":"015",
    //                         "invoice":id,
    //                         "consumption_no":id,
    //                         "stamp": formatDate(order_data.creation_date),
    //                         "consumption_amount":order_data.amount_total,
    //                         "trade_type":"Sale",
    //                         "trade_lineType":1,
    //                         "remarks":"",
    //                         "trade_amount":order_data.amount_total,
    //                         "consumption_list": consumption_list,
    //                         "pay_tools": pay_tools
    //                     }
    //                     console.log("Trade Data");
    //                     console.log(trade_data);
    //                     callRPC({
    //                         model: 'res.partner',
    //                         method: 'pms_process_trade',
    //                         args: [trade_data],
    //                     }).then(function (result) {
    //                         console.log("pms_process_trade");
    //                         console.log(result); 
    //                         var result_json = JSON.parse(result)    
    //                         console.log(result_json);               
    //                         if(result_json.err === true){
    //                             console.log(result_json.message);
    //                         }
    //                     }).then(function(err){
    //                         console.log(err);
    //                     });
    //                 }

    //             }
    //         }
    //     }else{
    //         console.log('Data not Array');
    //     }
        
    // }
});
