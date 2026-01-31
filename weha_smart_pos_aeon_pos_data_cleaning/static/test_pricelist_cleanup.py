# -*- coding: utf-8 -*-
"""
Utility script to test CouchDB pricelist cleanup
This script can be run directly from Python to test the cleanup functionality
without going through Odoo interface.

Usage:
    python test_pricelist_cleanup.py

Requirements:
    - requests library
    - Access to CouchDB server
"""

import requests
import json
from datetime import datetime, timedelta
from requests.auth import HTTPBasicAuth

# Configuration
COUCHDB_URL = "https://couchdb.server1601.weha-id.com"
COUCHDB_DATABASE = "s_7001_product_pricelist_items"  # Change according to branch
USERNAME = "admin"
PASSWORD = "pelang1"
RETENTION_DAYS = -7  # Keep for 7 days after date_end

def test_find_expired_pricelists():
    """Test finding expired pricelist items in CouchDB"""
    
    auth = HTTPBasicAuth(USERNAME, PASSWORD)
    headers = {'Content-Type': 'application/json'}
    
    # Calculate retention date
    current_date_time = datetime.now()
    retain_date_time = current_date_time + timedelta(days=RETENTION_DAYS)
    retain_date_str = retain_date_time.strftime('%Y-%m-%d')
    
    print(f"Looking for pricelist items with date_end before: {retain_date_str}")
    
    find_url = f"{COUCHDB_URL}/{COUCHDB_DATABASE}/_find"
    
    query = {
        "selector": {
            "date_end": {
                "$lt": retain_date_str
            }
        },
        "fields": ["_id", "_rev", "id", "date_start", "date_end"],
        "limit": 1000
    }
    
    try:
        response = requests.post(find_url, auth=auth, headers=headers, 
                                data=json.dumps(query), verify=False)
        
        if response.status_code == 200:
            response_json = response.json()
            docs = response_json.get("docs", [])
            
            print(f"\nFound {len(docs)} expired pricelist items:")
            print("-" * 80)
            
            for idx, doc in enumerate(docs, 1):
                print(f"{idx}. ID: {doc['_id']}")
                print(f"   Odoo ID: {doc.get('id', 'N/A')}")
                print(f"   Date Start: {doc.get('date_start', 'N/A')}")
                print(f"   Date End: {doc.get('date_end', 'N/A')}")
                print(f"   Rev: {doc['_rev']}")
                print()
            
            return docs
        else:
            print(f"Error querying CouchDB: {response.status_code}")
            print(f"Response: {response.text}")
            return []
    
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return []


def test_delete_single_document(doc_id, doc_rev):
    """Test deleting a single document from CouchDB"""
    
    auth = HTTPBasicAuth(USERNAME, PASSWORD)
    headers = {'Content-Type': 'application/json'}
    
    delete_url = f"{COUCHDB_URL}/{COUCHDB_DATABASE}/{doc_id}?rev={doc_rev}"
    
    try:
        response = requests.delete(delete_url, auth=auth, headers=headers, verify=False)
        
        if response.status_code in (200, 201):
            print(f"✓ Successfully deleted document: {doc_id}")
            return True
        else:
            print(f"✗ Failed to delete document {doc_id}: Status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"✗ Exception deleting document {doc_id}: {str(e)}")
        return False


def test_cleanup_all_expired(dry_run=True):
    """
    Test cleanup of all expired pricelist items
    
    :param dry_run: If True, only lists items without deleting them
    """
    
    print(f"\n{'=' * 80}")
    print(f"CouchDB Pricelist Cleanup Test")
    print(f"{'=' * 80}")
    print(f"CouchDB URL: {COUCHDB_URL}")
    print(f"Database: {COUCHDB_DATABASE}")
    print(f"Retention Days: {RETENTION_DAYS}")
    print(f"Mode: {'DRY RUN (no deletion)' if dry_run else 'LIVE (will delete)'}")
    print(f"{'=' * 80}\n")
    
    # Find expired items
    expired_docs = test_find_expired_pricelists()
    
    if not expired_docs:
        print("\nNo expired pricelist items found.")
        return
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE: No items will be deleted")
        print(f"   Set dry_run=False to actually delete {len(expired_docs)} items")
        return
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: About to delete {len(expired_docs)} items from CouchDB")
    confirm = input("Type 'YES' to confirm deletion: ")
    
    if confirm != 'YES':
        print("Deletion cancelled.")
        return
    
    # Delete items
    print(f"\nDeleting {len(expired_docs)} items...")
    print("-" * 80)
    
    deleted_count = 0
    failed_count = 0
    
    for doc in expired_docs:
        if test_delete_single_document(doc['_id'], doc['_rev']):
            deleted_count += 1
        else:
            failed_count += 1
    
    print("-" * 80)
    print(f"\nSummary:")
    print(f"  Total items: {len(expired_docs)}")
    print(f"  Successfully deleted: {deleted_count}")
    print(f"  Failed: {failed_count}")


if __name__ == "__main__":
    # Run in dry-run mode first to see what would be deleted
    test_cleanup_all_expired(dry_run=True)
    
    # Uncomment the line below to actually delete expired items
    # test_cleanup_all_expired(dry_run=False)
