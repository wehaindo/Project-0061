# Python program to read
# json file
 
import json
import xmlrpc.client
import csv


order_line_tmpl = {
    "qty": 1,
    "price_unit": 275000,
    "price_subtotal": 247748,
    "price_subtotal_incl": 275000,
    "discount": 0,
    "product_id": 392786,
    "tax_ids": [
        [
        6,
        False,
        [
            1
        ]
        ]
    ],
    "id": 1,
    "pack_lot_ids": [],
    "description": "",
    "full_product_name": "ANJASMARA ESSENTIAL OIL FRANKI",
    "price_extra": 0,
    "price_manually_set": False,
    "price_automatically_set": False,
    "price_source": "list_price",
    "list_price": 275000,
    "price_override_user": False,
    "price_override_reason": False,
    "prc_no": "",
    "discount_type": "",
    "discount_amount": 0,
    "uniqueParentId": False,
    "uniqueChildId": False,
    "isRuleApplied": False,
    "promotion": False,
    "combination_id": False,
    "parent_combination_id": False,
    "promotion_flag": False,
    "promotion_disc_parentId": False,
    "promotion_disc_childId": False,
    "product_uom": 1
}

order_tmpl = {
    "name": "Order 008630001",
    "amount_paid": 0,
    "amount_total": 519000,
    "amount_tax": 51432,
    "amount_return": 0,
    "lines": [],
    "statement_ids": [],
    "pos_session_id": 863,
    "pricelist_id": 2,
    "partner_id": False,
    "user_id": 10,
    "uid": "008630001",
    "sequence_number": 1,
    "creation_date": "2024-02-24T11:15:21.975Z",
    "fiscal_position_id": False,
    "server_id": False,
    "to_invoice": False,
    "to_ship": False,
    "is_tipped": False,
    "tip_amount": 0,
    "access_token": "367139ff-3c02-4ea2-81b3-b485e9f6ed6b",
    "is_void": False,
    "is_refund": False,
    "refund_parent_pos_reference": "",
    "void_parent_pos_reference": "",
    "is_aeon_member": False,
    "card_no": False,
    "aeon_member": False,
    "aeon_member_day": False,
    "is_void_order": False,
    "orderPromotion": False,
    "orderDiscountLine": False
}

server_url = 'https://pos.aeonindonesia.co.id'
database = 'aeondb'
user = 'admin'
password = 'f4d2dc2254c643a6f40ae79f67c847182d377868'
# password = '6a3efaf7ec0339016b6878bf96b0498aa0063d67' staging
common_auth = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(server_url))
uid = common_auth.authenticate(database, user, password, {})
print(uid)

data_model = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_url))
# Opening JSON file
f = open('601.json')
 
# returns JSON object as 
# a dictionary
data = json.load(f)
 
# Iterating through the json
# list
count = 0
import_json = {
    "unpaid_orders": [],
    "session": "POS/00863",
    "session_id": 863,
    "date": "Tue, 27 Feb 2024 01:43:23 GMT",
    "version": [
        16,
        0,
        0,
        "final",
        0,
        ""
    ]
}


unpaid_orders = []
lines = []
print('openfile')
with open("ForImport.csv", newline='') as csvfile:
    productreader = csv.reader(csvfile, delimiter=',')    
    price_subtotal_incl = 0.0
    for row in productreader:
        default_code = row[3].zfill(9)
        print(default_code)
        product_ids = data_model.execute_kw(database,uid,password,'product.template','search',[[['default_code','=',default_code]]],{})
        if product_ids:
            order_line = {
                "qty": 1,
                "price_unit": 275000,
                "price_subtotal": 247748,
                "price_subtotal_incl": 275000,
                "discount": 0,
                "product_id": 392786,
                "tax_ids": [
                    [
                    6,
                    False,
                    [
                        1
                    ]
                    ]
                ],
                "id": 1,
                "pack_lot_ids": [],
                "description": "",
                "full_product_name": "ANJASMARA ESSENTIAL OIL FRANKI",
                "price_extra": 0,
                "price_manually_set": False,
                "price_automatically_set": False,
                "price_source": "list_price",
                "list_price": 275000,
                "price_override_user": False,
                "price_override_reason": False,
                "prc_no": "",
                "discount_type": "",
                "discount_amount": 0,
                "uniqueParentId": False,
                "uniqueChildId": False,
                "isRuleApplied": False,
                "promotion": False,
                "combination_id": False,
                "parent_combination_id": False,
                "promotion_flag": False,
                "promotion_disc_parentId": False,
                "promotion_disc_childId": False,
                "product_uom": 1
            }
            order_line['product_id'] = product_ids[0]
            order_line['qty'] = -1 * int(float(row[8]))
            
            # print(product_ids[0])
            product_template_ids = data_model.execute_kw(database,uid,password, 'product.template','read', [product_ids[0]], {})
            order_line['full_product_name'] = product_template_ids[0]['name']
            # print(product_template_id)            
            product_template_price_ids = data_model.execute_kw(database,uid,password,'product.template.price','search',[[['res_branch_id','=',41],['product_template_id','=',product_ids[0]]]],{})
            if product_template_price_ids:
                product_template_price_id = data_model.execute_kw(database,uid,password, 'product.template.price','read', [product_template_price_ids], {})
                # print(product_template_price_id[0]['list_price'])
                # print(row[8])
                order_line['price_unit'] = int(product_template_price_id[0]['list_price'])
                order_line['list_price'] = int(product_template_price_id[0]['list_price'])
                current_price_subtotal_incl = order_line['price_unit'] * order_line['qty']
                order_line['price_subtotal_incl'] = current_price_subtotal_incl
                print('current_price_subtotal_incl')
                print(current_price_subtotal_incl)
                price_subtotal = int(current_price_subtotal_incl - (current_price_subtotal_incl * 0.11))
                order_line['price_subtotal'] = price_subtotal
                print('price_subtotal')               
                print(price_subtotal)                
                price_subtotal_incl = price_subtotal_incl + current_price_subtotal_incl                
            else:
                order_line['price_unit'] = int(product_template_ids[0]['list_price'])
                order_line['list_price'] = int(product_template_ids[0]['list_price'])                
                current_price_subtotal_incl = (int(product_template_ids[0]['list_price']) * int(float(row[8])))
                print('current_price_subtotal_incl')
                print(current_price_subtotal_incl)
                price_subtotal = current_price_subtotal_incl - (current_price_subtotal_incl * 0.11)
                order_line['price_subtotal'] = price_subtotal                
                print('price_subtotal') 
                print(price_subtotal)                
                price_subtotal_incl = price_subtotal_incl + current_price_subtotal_incl
            lines.append([0,0, order_line])
    order_tmpl['lines'] = lines
    unpaid_orders.append(order_tmpl)
    print(order_tmpl)
    print(price_subtotal_incl)

import_json['unpaid_orders'] = unpaid_orders
# Serializing json
json_object = json.dumps(import_json)
 
# Writing to sample.json
with open("import_file_from_csv.json", "w") as outfile:
    outfile.write(json_object)
#print(import_json)

# Closing file
f.close()