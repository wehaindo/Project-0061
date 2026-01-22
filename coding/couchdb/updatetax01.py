import requests
import json

# CouchDB credentials and database details
COUCHDB_URL = "https://couchdb.server1601.weha-id.com"
DB_NAME = "s_7001_products"
USERNAME = "admin"
PASSWORD = "pelang1"

# Define the startkey
startkey = "product"

# Fetch all documents
# response = requests.get(f"{COUCHDB_URL}/{DB_NAME}/_all_docs?include_docs=true", auth=(USERNAME, PASSWORD))
# Fetch documents using startkey
response = requests.get(
    f"{COUCHDB_URL}/{DB_NAME}/_all_docs",
    params={"startkey": json.dumps(startkey), "include_docs": "true"},
    auth=(USERNAME, PASSWORD),
)

if response.status_code != 200:
    print("Error fetching documents:", response.json())
    exit()

docs = response.json()['rows']

# Prepare the updated documents
updated_docs = []
for row in docs:
    doc = row['doc']
    if '_id' in doc and '_rev' in doc:
        # Update fields here
        doc['taxes_id'] = [12]
        updated_docs.append(doc)

# print(updated_docs)

# Serializing json
# json_object = json.dumps(updated_docs, indent=4)
 
# Writing to sample.json
# with open("sample.json", "w") as outfile:
#     outfile.write(json_object)
    
# Bulk update the documents
bulk_update_payload = {"docs": updated_docs}
bulk_update_response = requests.post(
    f"{COUCHDB_URL}/{DB_NAME}/_bulk_docs",
    auth=(USERNAME, PASSWORD),
    headers={"Content-Type": "application/json"},
    data=json.dumps(bulk_update_payload),
)

if bulk_update_response.status_code == 201:
    print("Documents updated successfully!")
else:
    print("Error updating documents:", bulk_update_response.json())
