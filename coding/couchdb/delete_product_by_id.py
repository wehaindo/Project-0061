import requests
import json

# CouchDB connection details
couchdb_url = 'https://couchdb.server1601.weha-id.com'
db_name = 's_7001_products'
username = 'admin'
password = 'pelang1'

db_url = f"{couchdb_url}/{db_name}"

# URL for the database
# db_url = f"{couchdb_url}/{db_name}/_all_docs"

# List of document IDs to fetch
doc_ids = [ "product_00046331-fe5d-4963-a913-78ab4af25891", "product_00062639-c454-4058-8670-218100d084b3"]

# Request payload
payload = {
    "keys": doc_ids
}

# Fetch documents by IDs
# response = requests.post(db_url, auth=(username, password),
#                          headers={'Content-Type': 'application/json'},
#                          data=json.dumps(payload))
response = requests.post(f"{db_url}/_all_docs?include_docs=true", auth=(username, password),
                         headers={'Content-Type': 'application/json'},
                         data=json.dumps(payload))

# Check if the request was successful
if response.status_code == 200:
    docs = response.json().get('rows', [])
    for doc in docs:
        print(doc)  # Each 'doc' contains 'id', 'key', 'value', and optionally 'doc' if "include_docs" is set
else:
    print("Failed to retrieve documents:", response.json())
