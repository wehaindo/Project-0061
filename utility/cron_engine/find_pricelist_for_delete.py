import requests
import json
from requests.auth import HTTPBasicAuth


auth = HTTPBasicAuth('admin','pelang1')
headers = {
    'Content-Type': 'application/json'                  
}   

url = "https://couchdb.server1601.weha-id.com/s_7001_product_pricelist_items/_find"

query = {   
    "selector": {
        "date_end": {"$lt": "2023-10-31"}
    },
    "fields": ["_id","_rev","id","date_start"],
    "limit": 1000
}

response = requests.post(url, auth=auth, headers=headers, data=json.dumps(query), verify=False)
if response.status_code == 200:
    response_json = response.json()
    docs = response_json["docs"]
    for doc in docs:
        print(doc['_id'] + " - " + doc['_rev'])
        delete_url =  "https://couchdb.server1601.weha-id.com/s_7001_product_pricelist_items/" + doc["_id"] + "?rev=" + doc["_rev"]
        delete_response = requests.delete(delete_url,auth=auth, headers=headers, verify=False)
        print(delete_response.status_code)
