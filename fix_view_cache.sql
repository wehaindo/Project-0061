-- SQL script to clear the cached view
-- Run this in PostgreSQL if you can't upgrade the module

-- Find the view ID
SELECT id, name, model FROM ir_ui_view 
WHERE name = 'pos.activity.log.search' 
  AND model = 'pos.activity.log';

-- Delete the view to force reload from XML
DELETE FROM ir_ui_view 
WHERE name = 'pos.activity.log.search' 
  AND model = 'pos.activity.log';

-- After running this, restart Odoo and the view will be recreated from XML
