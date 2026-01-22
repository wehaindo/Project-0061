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
url = "https://aeondb.server1601.weha-id.com"
db = "aeondb"
username = "admin"
password = "pelang123"

# Common endpoint
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

# Object endpoint
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# Check if authentication was successful
if uid:
    print(f"Authenticated as {username} (UID: {uid})")
    # Define search domain (e.g., search for products with name 'New Product')
    search_domain = [[['branch_ids','in',[41,42,43]],['taxes_id','in',[2]]]]
    
    # search_domain = [[['branch_ids','in',[41,42,43]],['default_code','=','001336016']]]

    # Search for products that match the search domain
    product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', search_domain)

    print(f"Found products with IDs: {len(product_ids)}")

    # Optionally, you can read data of the found products
    for product_id in product_ids: 
        print(product_id)
        products = models.execute_kw(db, uid, password, 'product.template', 'read', [product_id])
        # print(products[0]['taxes_id'])
        # for i in range(len(products[0]['taxes_id'])):    
            # if products[0]['taxes_id'][i] == 2:
        try:
            taxes_id = [(6, 0, [11])]        
            models.execute_kw(db, uid, password, 'product.template', 'write', [[product_id],{'taxes_id': taxes_id}])                        
            print('Update Taxes ID')
        except Exception as ex:
            print(ex)
else:
    print("Authentication failed.")