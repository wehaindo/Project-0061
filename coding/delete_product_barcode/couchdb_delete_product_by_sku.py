import requests
from requests.auth import HTTPBasicAuth
import json

def specific_string(length):  
    sample_string = 'pqrstuvwxy' # define the specific string  
    # define the condition for random string  
    result = ''.join((random.choice(sample_string)) for x in range(length))  
    print(" Randomly generated string is: ", result)
    return result

default_codes = []
# Open the file in read mode
with open('productsku.txt', 'r') as file:
    # Read each line in the file
    for line in file:
        # Print each line
        default_codes.append("0" + line.replace('\n', ''))

print(default_codes)
# Odoo connection details
url = "https://aeondb.server1601.weha-id.com"
# couchdb_server_url = "https://couchdb.aeonindonesia.co.id"
couchdb_name = "s_7001_product_barcode"
username = "admin"
password = "pelang1"

auth = HTTPBasicAuth(username,password)
headers = {
    'Content-Type': 'application/json'                  
}      


query_payload = {
    "selector": {
        "default_code": {
            "$in" : default_codes 
        }
    }                
}
# print(query_payload)
response = requests.post(f'{couchdb_server_url}/{couchdb_name}/_find', auth=auth, headers=headers, data=json.dumps(query_payload), verify=False)
if response.status_code == 200:
    docs_to_delete = []    
    print("Query successful. Results:")
    docs = response.json().get("docs", [])
    print(docs)
    count = len(response.json().get("docs", []))
    print(count)
    
    # for doc in response.json().get("docs", []):
    #     docs_to_delete.append({"_id": doc["_id"], "_rev": doc["_rev"], "_deleted": True})    
    # # print(docs_to_delete)
    
    # bulk_delete_payload = {
    #     "docs": docs_to_delete
    # }
    # response = requests.post(
    #     f"{couchdb_server_url}/{couchdb_name}/_bulk_docs",
    #     auth=auth,
    #     headers=headers,
    #     data=json.dumps(bulk_delete_payload),
    #     verify=False
    # )

    # if response.status_code == 201:
    #     print("Bulk deletion successful. Results:")
    #     for result in response.json():
    #         print(result)
    # else:
    #     print("Bulk deletion failed:", response.json())
else:
    print("Query failed:", response.json())



