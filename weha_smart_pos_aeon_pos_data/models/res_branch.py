from odoo import models, fields



class ResBranch(models.Model):
    _inherit = 'res.branch'

    def action_product_store_update(self):
        pass 

    def action_product_product_couchdb_sync(self):
        pass

    def action_product_categories_couchdb_sync(self):
        pass

    def action_product_pricelist_item_couchdb_sync(self):
        pass 

    
    # couchdb_server_url = fields.Char('CouchDB Server')
    # couchdb_name = fields.Char('Product DB')
    couchdb_product_categories = fields.Char('Product Categories DB')
    couchdb_product_pricelist_items = fields.Char('Pricelist Items DB')
    couchdb_product_barcode = fields.Char('Product Barcode DB')
    # couchdb_pos_order = fields.Char('Pos Orders DB')
