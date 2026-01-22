import pandas as pd
import json

# Load Excel file
xls = pd.ExcelFile('20250511.xlsx')
orders_df = pd.read_excel(xls, 'Order')
details_df = pd.read_excel(xls, 'OrderDetail')

# Convert to nested JSON
# result = []
# {
#   "name": "015200001",
#   "amount_paid": 14800,
#   "amount_total": 14800,
#   "amount_tax": 1467,
#   "amount_return": 0,
#   "pos_session_id": 1520,
#   "pricelist_id": 2,
#   "partner_id": 37,
#   "user_id": 35,
#   "lines": [
#     {
#       "qty": 1,
#       "price_unit": 14800,
#       "price_subtotal": 13333,
#       "price_subtotal_incl": 14800,
#       "discount": "0",
#       "product_id": 440526,
#       "tax_ids": [
#         1
#       ],
#       "full_product_name": "GLICO HAKU MONAKA VANILLA 180M",
#       "price_source": "list_price",
#       "list_price": 14800,
#       "prc_no": "",
#       "discount_type": "",
#       "discount_amount": 0,
#       "product_uom": 1
#     }
#   ],
#   "statement_ids": [
#     {
#       "name": "2025-05-14 16:58:04",
#       "payment_method_id": 16,
#       "amount": 14800,
#       "payment_status": "00-success",
#       "merchant_id": "998224064771654",
#       "terminal_id": "DSP00002",
#       "is_prima": "true",
#       "partner_reference_no": "513416577846",
#       "reference_no": "513416577846",
#       "external_id": "89476168218947616821",
#       "transaction_date": "2025-05-14T09:58:04.089Z",
#       "service_code": "682468f11fc5c7b952a025d7",
#       "invoice_number": "89476168218947616821",
#       "refund_time": ""
#     }
#   ],
#   "sequence_number": 1,
#   "creation_date": "2025-05-14T09:58:04.089Z",
#   "is_aeon_member": false,
#   "card_no": "",
#   "aeon_member": false,
#   "aeon_member_day": false,
#   "access_token": ""
# }

pos_session_id=0
pricelist_id=2
user_id=2
for _, order in orders_df.iterrows():
    order_id = order['order_id']
    details = details_df[details_df['order_id'] == order_id].drop(columns=['order_id'])
    amount_tax = 0
    lines = []
    for detail in details:
        line = {
            "qty": detail['qty'],
            "price_unit": detail['price_unit'],
            "price_subtotal": detail['price_subtotal'],
            "price_subtotal_incl": detail['price_subtotal_inc'],
            "discount": 0,
            "product_id": 440526,
            "tax_ids": [
                1
            ],
            "full_product_name": detail['product_name'],
            "price_source": "list_price",
            "list_price": 14800,
            "prc_no": "",
            "discount_type": "",
            "discount_amount": 0,
            "product_uom": 1
        }
    lines.append(line)
            
    result.append({
        "name": order_id['name'],
        "amount_paid": order_id['amount'],
        "amount_total": order_id['amount'],
        "amount_tax": amount_tax,
        "amount_return": 0,
        "pos_session_id": pos_session_id,
        "pricelist_id": pricelist_id,
        "partner_id": false,
        "user_id": user_id,
        "OrderID": str(order_id),        
        "OrderDate": str(order['ORDER DATETIME']),
        "Details": details.to_dict(orient='records')
    })

# Save to JSON file
with open('orders.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Conversion complete. File saved as orders.json")
