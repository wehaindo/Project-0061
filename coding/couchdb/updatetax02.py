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
count = 0
for row in docs:
    count = count + 1
    doc = row['doc']
    # print(doc)
    response = requests.get(f"{COUCHDB_URL}/{DB_NAME}/{doc['_id']}", auth=(USERNAME, PASSWORD))
    if response.status_code != 200:
        print("Error fetching document:", response.json())
        exit()

    doc = response.json()

    # Step 2: Modify the document
    doc["taxes_id"] = [11]  # Update the field

    # Step 3: Save the updated document
    update_response = requests.put(
        f"{COUCHDB_URL}/{DB_NAME}/{doc['_id']}",
        json=doc,
        auth=(USERNAME, PASSWORD),
    )

    if update_response.status_code == 201:
        print("Count : ", count)
        #print("Document updated successfully:", update_response.json())        
    else:
        print("Error updating document:", update_response.json())
