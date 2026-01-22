import xmlrpc.client
import random  
import string  

def specific_string(length):  
    sample_string = 'pqrstuvwxy' # define the specific string  
    # define the condition for random string  
    result = ''.join((random.choice(sample_string)) for x in range(length))  
    print(" Randomly generated string is: ", result)
    return result

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

# Check if authentication was successful
if uid:
    print(f"Authenticated as {username} (UID: {uid})")

    for i in range(500000):
            
        # Prepare product data
        product_data = {
            'name': specific_string(10),
            'type': 'product',  # 'product' for storable products, 'consu' for consumables, 'service' for services
            'list_price': 100.0,  # Set product price
            'default_code': specific_string(10),  # Internal reference (SKU)
            'categ_id': 1,  # Product category (default: 1 for 'All')
            'uom_id': 1,  # Unit of measure (default: 1 for 'Unit(s)')
            'uom_po_id': 1,  # Purchase unit of measure (default: 1 for 'Unit(s)')
            'available_in_pos': True, # Available In Pos
        }
        print(product_data)
        # Create product in Odoo
        product_id = models.execute_kw(db, uid, password, 'product.template', 'create', [product_data])
        print(f"Product created with ID: {product_id}")
else:
    print("Authentication failed.")