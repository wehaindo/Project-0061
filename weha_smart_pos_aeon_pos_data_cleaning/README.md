# WEHA Smart POS - AEON POS Data Cleaning

## Overview
This module provides automated cleaning functionality for CouchDB data, specifically targeting expired product pricelist items that should no longer be retained in the CouchDB database.

## Features

### 1. Automated CouchDB Cleanup for Expired Pricelists
- **Purpose**: Automatically removes expired `product.pricelist.item` records from CouchDB after a configurable retention period
- **Important**: Only cleans data from CouchDB, NOT from Odoo database
- **Scheduled Job**: Runs daily by default via cron job

### 2. Configurable Retention Period
- Navigate to: **Settings → Point of Sale → POS Data Cleaning**
- Configure **Pricelist Retention Days** (default: -7 days)
- The retention period is counted from the `date_end` field of pricelist items
- Example: `-7` means pricelist items will be deleted from CouchDB 7 days after their `date_end`

### 3. Manual Cleanup Option
- A manual cleanup button is available on the pricelist item form
- Only visible to System Administrators
- Allows immediate cleanup without waiting for the scheduled job

## Configuration

### Setting up the Retention Period
1. Go to **Settings → Point of Sale**
2. Scroll to **POS Data Cleaning** section
3. Set **Pricelist Retention Days** (use negative values)
   - `-7`: Keep for 7 days after expiry
   - `-30`: Keep for 30 days after expiry
   - `0`: Delete immediately upon expiry
4. Click **Save**

### Enabling/Disabling Automatic Cleanup
1. Go to **Settings → Technical → Automation → Scheduled Actions**
2. Find **Clean Expired Pricelist Items from CouchDB**
3. Toggle the **Active** checkbox
4. Adjust the schedule if needed (default: daily)

## Technical Details

### How it Works
1. The cron job runs daily (configurable)
2. For each branch with CouchDB configuration:
   - Queries CouchDB for pricelist items with `date_end < (current_date + retention_days)`
   - Deletes matching documents from CouchDB using the CouchDB REST API
   - Logs all operations for audit purposes

### CouchDB Query
The module uses CouchDB's `_find` endpoint with the following selector:
```json
{
  "selector": {
    "date_end": {
      "$lt": "2024-01-23"  // calculated based on retention_days
    }
  }
}
```

### Security
- Manual cleanup button: `base.group_system` (System Administrators only)
- Cron job: Runs with system privileges
- CouchDB authentication: Uses configured credentials from branch settings

### Logging
All cleanup operations are logged with detailed information:
- Branch being processed
- Number of expired items found
- Successfully deleted items with their IDs and date_end
- Any errors encountered

## Dependencies
- `point_of_sale`: Core POS module
- `weha_smart_pos_aeon_pos_data`: Parent module with CouchDB integration

## Important Notes

⚠️ **Critical Points**:
1. **This module ONLY cleans CouchDB data**, not Odoo database records
2. **Cannot be undone**: Once deleted from CouchDB, data cannot be recovered
3. **Requires CouchDB configuration** on branch level:
   - `couchdb_server_url`
   - `couchdb_product_pricelist_items` (database name)
4. **Network connectivity**: Requires access to CouchDB server

## Troubleshooting

### No items are being cleaned
- Check if cron job is active
- Verify retention period configuration
- Check CouchDB connection from branches
- Review logs for errors

### CouchDB connection errors
- Verify branch CouchDB settings
- Check network connectivity
- Verify CouchDB credentials
- Check CouchDB server status

### Finding logs
- Go to **Settings → Technical → Logging**
- Filter by model: `product.pricelist.item`
- Search for: "expired pricelist" or "CouchDB"

## Support
For support, contact: weha.consultant@gmail.com
Website: https://www.weha-id.com

## License
LGPL-3

## Version History
- **16.0.1.0**: Initial release with automated pricelist cleanup from CouchDB
