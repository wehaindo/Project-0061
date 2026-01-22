import xmlrpc.client
import random  
import string  

# Odoo connection details
url = "https://sarinah.saas1601.weha-id.com"
db = "sarinah"
username = "admin"
password = "pelang1"

# Common endpoint
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

# Object endpoint
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Branch
branch_id = 1

# Check if authentication was successful
if uid:
    print(f"Authenticated as {username} (UID: {uid})")

    # Define search domain (e.g., search for products with name 'New Product')
    search_domain = [[]]

    # Search for products that match the search domain
    product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', search_domain)

    # print(f"Found products with IDs: {product_ids}")

    # Optionally, you can read data of the found products
    for product_id in product_ids: 
        search_domain = [['branch_id','=',branch_id],['product_template_id','=',product_id]]
        print(search_domain)
        product_template_couchdb_ids = models.execute_kw(db, uid, password, 'product.template.couchdb', 'search', [search_domain])
        if len(product_template_couchdb_ids) == 0:
            vals = {
                'branch_id': branch_id,
                'product_template_id': product_id,
                'list_price': 100
            }
            print(vals)
            product_template_couchdb_id = models.execute_kw(db, uid, password, 'product.template.couchdb', 'create', [vals])
            print(f"Product Template CouchDb created with ID: {product_template_couchdb_id}")
