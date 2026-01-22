from concurrent.futures import ThreadPoolExecutor
import requests
import json

# CouchDB configuration
COUCHDB_URL = "https://couchdb.server1601.weha-id.com"
DATABASE_NAME = "s_7001_products"
USERNAME = "admin"
PASSWORD = "pelang1"
VIEW_URL = f"{COUCHDB_URL}/{DATABASE_NAME}/_design/taxesId11/_view/taxesId11-view"

def update_docs(batch):
    url = f"{COUCHDB_URL}/{DATABASE_NAME}/_bulk_docs"
    headers = {"Content-Type": "application/json"}
    data = {"docs": batch}
    response = requests.post(url, auth=(USERNAME, PASSWORD), headers=headers, data=json.dumps(data))    
    # print(response.text)
    return response.json()


# Parameters for the query
params = {
    "include_docs": "true"  # Include the full document content
}

# Send the GET request
response = requests.get(VIEW_URL, params=params, auth=(USERNAME, PASSWORD))

# Check the response
if response.status_code == 200:
    # result = response.json()
    rows = response.json()['rows']
    # Divide documents into batches
    batch_size = 500
    # batches = [docs[i:i+batch_size] for i in range(0, len(docs), batch_size)]
    batches = [
        [{**row["doc"], "taxes_id": [11]} for row in rows[i:i + batch_size]]
        for i in range(0, len(rows), batch_size)
    ]
    
    print(len(batches))
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(update_docs, batches)
    print("Updates completed!")
    
    # print(result)
    #  baris = 0
    # for row in result.get("rows", []):
    #     baris = baris + 1
    #     print(f"{baris} - Document ID: {row['id']}")
    #     # print(f"Document: {row['doc']}")
else:
    print(f"Failed to query the view: {response.status_code}")
    # print(response.text)
