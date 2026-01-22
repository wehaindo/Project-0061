import requests

# CouchDB configuration
# COUCHDB_URL = "https://couchdb.server1601.weha-id.com"
COUCHDB_URL = "https://couchdb.aeonindonesia.co.id"
DATABASE_NAME = "s_7004_products"
USERNAME = "admin"
PASSWORD = "pelang1"
VIEW_URL = f"{COUCHDB_URL}/{DATABASE_NAME}/_design/taxesId12/_view/taxesId12-view"

# Parameters for the query
params = {
    "include_docs": "true"  # Include the full document content
}

# Send the GET request
response = requests.get(VIEW_URL, params=params, auth=(USERNAME, PASSWORD), verify=False)

# Check the response
if response.status_code == 200:
    result = response.json()
    # print(result)
    baris = 0
    for row in result.get("rows", []):
        baris = baris + 1
        print(f"{baris} - Document ID: {row['id']}")
        # print(f"Document: {row['doc']}")
else:
    print(f"Failed to query the view: {response.status_code}")
    print(response.text)
