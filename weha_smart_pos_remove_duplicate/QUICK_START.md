# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install the Module (2 minutes)

1. Open Odoo
2. Go to **Apps**
3. Click **Update Apps List**
4. Search for **"Remove Duplicate"**
5. Click **Install**

### Step 2: Check for Duplicates (1 minute)

**Option A: Use the Wizard**
1. Go to **Point of Sale → Remove Duplicate Order Lines**
2. Leave filters empty (or add access token if you want)
3. Click **"Scan for Duplicates"**
4. Review the results

**Option B: Use the Order List**
1. Go to **Point of Sale → Orders**
2. Click on **Filters** → **With Duplicates**
3. See all orders that have duplicate lines

### Step 3: Remove Duplicates (2 minutes)

**From Wizard:**
1. After scanning, click **"Remove Duplicates"**
2. Confirm the results
3. Done! ✅

**From Order Form:**
1. Open any order with duplicates
2. Click the **"Remove Duplicates"** button at the top
3. Done! ✅

---

## 📋 Quick Examples

### Example 1: Remove All Duplicates (One Click)
```
1. Point of Sale → Remove Duplicate Order Lines
2. Click "Scan and Remove" button
3. Done!
```

### Example 2: Remove Duplicates for Specific Access Token
```
1. Point of Sale → Remove Duplicate Order Lines
2. Enter access token: "abc123xyz"
3. Click "Scan and Remove"
4. Done!
```

### Example 3: Automatic Cleanup (Set It and Forget It)
```
1. Settings → Technical → Scheduled Actions
2. Search: "Remove Duplicate POS Order Lines"
3. Set Active = True
4. Done! Runs daily automatically
```

---

## 🎯 Common Use Cases

### Use Case 1: Daily Cleanup
**Scenario:** You want to automatically clean duplicates every night

**Solution:**
1. Activate the cron job
2. Set time to run during off-peak hours
3. Check logs next morning

### Use Case 2: Before Month-End Reports
**Scenario:** Clean data before generating reports

**Solution:**
1. Run wizard with "Scan and Remove"
2. Verify results
3. Generate reports

### Use Case 3: Specific Order Issues
**Scenario:** Customer reports wrong total on specific order

**Solution:**
1. Open the order
2. Check if it has duplicates (indicator will show)
3. Click "Remove Duplicates"
4. Total recalculates automatically

---

## ❓ Quick FAQ

**Q: Will it delete my orders?**
A: No! It only removes duplicate ORDER LINES, not orders. And only the duplicate ones.

**Q: How does it know what's a duplicate?**
A: Lines with same product, price, discount, and taxes are considered duplicates.

**Q: What if I make a mistake?**
A: Always backup first! But the module only removes true duplicates, keeping the first occurrence.

**Q: Can I undo?**
A: No automatic undo. That's why we recommend scanning first, then removing.

**Q: Is it safe?**
A: Yes, but always test on staging first and backup production before first use.

---

## 🎓 Tips & Tricks

### Tip 1: Scan Before Removing
Always use the two-step process (Scan → Remove) for important data.

### Tip 2: Filter by Access Token
If you know specific orders have issues, filter by access token.

### Tip 3: Check Logs
After removal, check Odoo logs to see what was removed:
```
grep "duplicate" /var/log/odoo/odoo.log
```

### Tip 4: Schedule Wisely
Run cron jobs during off-peak hours (like 2 AM).

### Tip 5: Monitor Results
After automated runs, check the results:
- Point of Sale → Orders with Duplicates
- Should be empty if all cleaned

---

## 🔧 Quick Troubleshooting

**Problem: No duplicates found**
- Check if orders have access_token
- Verify lines are truly identical (product, price, discount, taxes)

**Problem: Button not showing**
- Refresh the page
- Check if order actually has duplicates

**Problem: Can't access wizard**
- Check your user has POS User or POS Manager role

**Problem: Cron not running**
- Verify it's set to Active
- Check logs for errors
- Verify user permissions

---

## 📞 Need Help?

1. **Check Documentation:**
   - README.md (full user guide)
   - DEVELOPER.md (technical details)

2. **Check Logs:**
   - Settings → Technical → Logs
   - Filter by "duplicate"

3. **Contact Support:**
   - Weha Support Team
   - www.weha-id.com

---

## ✅ Success Checklist

After installation, verify:
- [ ] New menu items appear in Point of Sale
- [ ] Can open wizard
- [ ] Can see duplicate indicators in order list
- [ ] Can remove duplicates from order form
- [ ] Logs show activity

---

## 🎉 You're Ready!

The module is now installed and ready to use. Start by scanning for duplicates to see if you have any issues in your database.

**Remember:**
- Backup first
- Test on staging
- Scan before removing
- Monitor results

**Happy cleaning! 🧹**
