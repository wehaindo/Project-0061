from concurrent.futures import ThreadPoolExecutor
import requests
import json


# CouchDB credentials and database details
COUCHDB_URL = "https://couchdb.server1601.weha-id.com"
DB_NAME = "s_7001_products"
USERNAME = "admin"
PASSWORD = "pelang1"


def update_docs(batch):
    url = f"{COUCHDB_URL}/{DB_NAME}/_bulk_docs"
    headers = {"Content-Type": "application/json"}
    data = {"docs": batch}
    response = requests.post(url, auth=(USERNAME, PASSWORD), headers=headers, data=json.dumps(data))
    return response.json()

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

# Divide documents into batches
batch_size = 500
# batches = [docs[i:i+batch_size] for i in range(0, len(docs), batch_size)]
batches = [
    [{**doc["doc"], "taxes_id": [1]} for doc in docs[i:i + batch_size]]
    for i in range(0, len(docs), batch_size)
]
    
# Serializing json
# json_object = json.dumps(batches, indent=4)
 
# Writing to sample.json
# with open("batches.json", "w") as outfile:
#     outfile.write(json_object)

# # Use ThreadPoolExecutor to process batches in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(update_docs, batches)
        
print("Updates completed!")