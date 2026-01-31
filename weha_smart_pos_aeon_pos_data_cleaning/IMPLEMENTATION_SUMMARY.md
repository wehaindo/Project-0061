# CouchDB Pricelist Cleanup - Implementation Summary

## Overview
This document provides a comprehensive summary of the CouchDB pricelist cleaning feature implemented in the `weha_smart_pos_aeon_pos_data_cleaning` module.

## What Was Implemented

### 1. Automated Cleanup System
**File**: `models/product_pricelist.py`

Created methods to automatically clean expired `product.pricelist.item` records from CouchDB:

- `_cron_clean_expired_pricelist_from_couchdb()`: Main cron method that runs scheduled cleanup
- `clean_expired_pricelist_items_by_branch()`: Cleans expired items for a specific branch
- `action_manual_clean_expired_pricelist()`: Manual cleanup trigger for administrators

**Key Features**:
- Queries CouchDB using `_find` endpoint to locate expired pricelists
- Only deletes from CouchDB, NOT from Odoo database
- Respects configurable retention period
- Comprehensive error handling and logging
- Multi-branch support

### 2. Configuration System
**File**: `models/res_config_settings.py`

Added configuration option in POS Settings:
- `pricelist_retention_days`: Configurable retention period (default: -7 days)
- Stored as system parameter: `weha_smart_pos.pricelist_retention_days`

### 3. Scheduled Action (Cron Job)
**File**: `data/ir_cron_data.xml`

Created automated task:
- **Name**: Clean Expired Pricelist Items from CouchDB
- **Schedule**: Daily (configurable)
- **Model**: product.pricelist.item
- **Method**: _cron_clean_expired_pricelist_from_couchdb()
- **Status**: Active by default

### 4. User Interface

#### Configuration View
**File**: `views/res_config_settings_view.xml`

Added settings section in POS Configuration:
- Path: Settings → Point of Sale → POS Data Cleaning
- Field: Pricelist Retention Days
- Description and help text included

#### Manual Cleanup Button
**File**: `views/product_pricelist_view.xml`

Added button to pricelist item form:
- Button: "Clean Expired from CouchDB"
- Location: Form header
- Access: System Administrators only (`base.group_system`)
- Shows success notification after execution

### 5. Documentation

#### README.md
Comprehensive documentation including:
- Feature overview
- Configuration instructions
- Technical details
- Troubleshooting guide
- Security considerations
- Version history

#### Test Script
**File**: `static/test_pricelist_cleanup.py`

Standalone Python script for testing:
- Can run independently of Odoo
- Dry-run mode to preview deletions
- Manual deletion with confirmation
- Detailed logging and reporting

## How It Works

### Cleanup Process Flow

1. **Trigger** (Daily via cron or Manual button click)
   ↓
2. **Get Configuration** (retention_days from system parameters)
   ↓
3. **Calculate Retention Date** (current_date + retention_days)
   ↓
4. **For Each Branch**:
   - Check CouchDB configuration exists
   - Query CouchDB for expired items (date_end < retention_date)
   - For each expired item:
     * Delete from CouchDB using REST API
     * Log success/failure
   ↓
5. **Summary** (Log total deleted items per branch)

### CouchDB Query Example

```json
{
  "selector": {
    "date_end": {
      "$lt": "2024-01-23"
    }
  },
  "fields": ["_id", "_rev", "id", "date_start", "date_end"],
  "limit": 1000
}
```

### Deletion Example

```
DELETE: https://couchdb.server/s_7001_product_pricelist_items/productpricelistitem_12345?rev=2-xyz
```

## Configuration

### Default Settings
- **Retention Days**: -7 (keep for 7 days after date_end)
- **Cron Schedule**: Daily at midnight
- **Cron Status**: Active
- **Batch Size**: 1000 items per query

### Customization Options

1. **Change Retention Period**:
   - Navigate to: Settings → Point of Sale → POS Data Cleaning
   - Modify "Pricelist Retention Days"
   - Examples:
     * `-7`: 7 days after expiry
     * `-30`: 30 days after expiry
     * `0`: Delete immediately upon expiry

2. **Adjust Cron Schedule**:
   - Navigate to: Settings → Technical → Scheduled Actions
   - Find: "Clean Expired Pricelist Items from CouchDB"
   - Modify interval (daily/weekly/monthly)

3. **Disable Automatic Cleanup**:
   - Navigate to: Settings → Technical → Scheduled Actions
   - Find: "Clean Expired Pricelist Items from CouchDB"
   - Uncheck "Active"

## Security Considerations

### Access Control
- **Manual cleanup button**: System Administrators only
- **Cron job**: Runs with system privileges
- **Configuration**: Accessible to users with Settings access

### Data Safety
- ⚠️ **Critical**: Only deletes from CouchDB, not from Odoo
- ⚠️ **Warning**: Deletion is permanent and cannot be undone
- ✓ **Safe**: Odoo database records remain intact for historical tracking

### Network Security
- Uses HTTPS for CouchDB connections (verify=False for self-signed certs)
- Authentication: HTTPBasicAuth with configured credentials
- Connection errors are caught and logged

## Dependencies

### Required Modules
1. `point_of_sale` (Odoo core)
2. `weha_smart_pos_aeon_pos_data` (parent module)

### Required Configuration (per branch)
- `couchdb_server_url`: Full URL to CouchDB server
- `couchdb_product_pricelist_items`: Database name for pricelist items
- Network connectivity to CouchDB server

### Python Libraries
- `requests`: HTTP client for CouchDB API
- `simplejson`: JSON serialization
- Standard library: `datetime`, `timedelta`, `logging`

## Testing

### Manual Testing Steps

1. **Verify Configuration**:
   ```
   Settings → Point of Sale → POS Data Cleaning
   Check: Pricelist Retention Days = -7
   ```

2. **Check Cron Job**:
   ```
   Settings → Technical → Scheduled Actions
   Find: "Clean Expired Pricelist Items from CouchDB"
   Verify: Active = True
   ```

3. **Test Manual Cleanup**:
   ```
   Go to: Product → Pricelist → Pricelist Items
   Open any pricelist item
   Click: "Clean Expired from CouchDB" button
   Check: Success notification appears
   ```

4. **Review Logs**:
   ```
   Settings → Technical → Logging
   Filter: model = product.pricelist.item
   Search: "expired pricelist"
   ```

### Using Test Script

```bash
# Navigate to module directory
cd weha_smart_pos_aeon_pos_data_cleaning/static/

# Edit configuration in test_pricelist_cleanup.py:
# - COUCHDB_URL
# - COUCHDB_DATABASE
# - USERNAME/PASSWORD
# - RETENTION_DAYS

# Run dry-run mode (no deletion)
python test_pricelist_cleanup.py

# Run live mode (actual deletion) - uncomment last line in script
# test_cleanup_all_expired(dry_run=False)
```

## Monitoring and Logs

### What Gets Logged

1. **Cron Start/End**:
   ```
   Starting scheduled cleanup of expired pricelist items from CouchDB
   Completed scheduled cleanup of expired pricelist items from CouchDB
   ```

2. **Branch Processing**:
   ```
   Processing branch: Store Name (ID: 123)
   Cleaning pricelist items with date_end before: 2024-01-23
   Found 45 expired pricelist items in CouchDB for branch Store Name
   ```

3. **Individual Deletions**:
   ```
   Deleted expired pricelist item: productpricelistitem_12345 (date_end: 2024-01-15)
   ```

4. **Errors**:
   ```
   Error cleaning expired pricelist for branch Store Name: [error details]
   Failed to delete pricelist item doc123: Status 409
   ```

### Finding Logs

**Via Odoo UI**:
```
Settings → Technical → Logging
Filter by:
- Model: product.pricelist.item
- Message contains: "expired pricelist"
```

**Via Server Logs**:
```
grep "expired pricelist" /var/log/odoo/odoo.log
```

## Troubleshooting

### Issue: No Items Being Cleaned

**Possible Causes**:
1. Cron job is not active
2. No expired items exist in CouchDB
3. Retention period too long
4. CouchDB connection issues

**Solutions**:
1. Check cron job active status
2. Run test script to verify expired items exist
3. Adjust retention period in settings
4. Verify CouchDB configuration on branches

### Issue: CouchDB Connection Errors

**Possible Causes**:
1. Incorrect CouchDB URL
2. Wrong database name
3. Invalid credentials
4. Network connectivity issues
5. CouchDB server down

**Solutions**:
1. Verify branch CouchDB settings
2. Test connection manually: `curl -X GET https://couchdb-url/db-name`
3. Check credentials
4. Verify network/firewall rules
5. Check CouchDB server status

### Issue: Permission Denied

**Possible Causes**:
1. User lacks system administrator rights
2. CouchDB credentials invalid

**Solutions**:
1. Grant system administrator access
2. Update CouchDB credentials in branch settings

## File Structure

```
weha_smart_pos_aeon_pos_data_cleaning/
├── __init__.py                          # Module init
├── __manifest__.py                      # Module manifest
├── README.md                            # User documentation
├── IMPLEMENTATION_SUMMARY.md            # This file
├── data/
│   └── ir_cron_data.xml                # Cron job definition
├── models/
│   ├── __init__.py                     # Models init
│   ├── product_pricelist.py            # Main cleanup logic
│   ├── product_product.py              # Existing product model
│   ├── product_category.py             # Existing category model
│   └── res_config_settings.py          # Configuration model
├── views/
│   ├── product_pricelist_view.xml      # Pricelist view with button
│   ├── product_product_view.xml        # Existing product view
│   └── res_config_settings_view.xml    # Settings view
├── security/
│   └── ir.model.access.csv             # Access rights
└── static/
    └── test_pricelist_cleanup.py       # Test script
```

## Next Steps / Future Enhancements

### Potential Improvements

1. **Enhanced Monitoring**:
   - Dashboard showing cleanup statistics
   - Email notifications after cleanup
   - Cleanup history report

2. **Batch Processing**:
   - Process in smaller batches to avoid timeouts
   - Pagination for large datasets (>1000 items)

3. **Additional Cleanup Targets**:
   - Expired promotions
   - Old product data
   - Obsolete categories

4. **Performance Optimization**:
   - Parallel processing for multiple branches
   - Bulk delete operations
   - Incremental cleanup throughout the day

5. **Backup/Recovery**:
   - Backup expired items before deletion
   - Recovery mechanism for accidental deletion
   - Archive to separate database

## Support and Maintenance

### Contact Information
- **Email**: weha.consultant@gmail.com
- **Website**: https://www.weha-id.com

### Version Information
- **Module Version**: 16.0.1.0
- **Odoo Version**: 16.0
- **License**: LGPL-3

### Change Log

**Version 16.0.1.0** (2024-01-30)
- Initial implementation
- Automated CouchDB cleanup for expired pricelists
- Configurable retention period
- Manual cleanup option
- Comprehensive logging
- Multi-branch support

---

**Implementation Date**: January 30, 2024
**Implemented By**: WEHA Consultant
**Status**: Complete and Ready for Testing
