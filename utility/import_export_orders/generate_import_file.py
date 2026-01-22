# Python program to read
# json file
 
import json
import xmlrpc.client

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
    "paid_orders": [],
    "session": "POS/01227",
    "session_id": 1227,
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
paid_orders = []
for i in data:
    access_token = i['access_token']
    pos_order_ids = data_model.execute_kw(database,uid,password,'pos.order','search',[[['access_token','=',access_token]]],{})
    if not pos_order_ids:
        count = count + 1
        print(count)
        id = i['name'].split(" ")[1]
        i['pos_session_id'] = import_json['session_id']
        vals = {
            "id": id,
            "data": i,
            "to_invoice": False
        }
        paid_orders.append(vals)
        #print(pos_order_ids)

import_json['paid_orders'] = paid_orders
# Serializing json
json_object = json.dumps(import_json)
 
# Writing to sample.json
with open("import_file.json", "w") as outfile:
    outfile.write(json_object)
#print(import_json)

 
# Closing file
f.close()