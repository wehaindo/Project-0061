import xmlrpc.client
import random  
import string  
import json

def specific_string(length):  
    sample_string = 'pqrstuvwxy' # define the specific string  
    # define the condition for random string  
    result = ''.join((random.choice(sample_string)) for x in range(length))  
    print(" Randomly generated string is: ", result)
    return result

default_codes = [
"007195501",
"001192049",
"001099331",
"000871136",
"000871136",
"002401232",
"002401232",
"007702150",
"007541957",
"008757975",
"008758026",
"008758002",
"001089615",
"008929334",
"001205190",
"001205190",
"008669964",
"007755262",
"007755231",
"009052918",
"007144066",
"007959486",
"008053435"
]

# Odoo connection details
# url = "https://aeondb.server1601.weha-id.com"
url = "https://pos.aeonindonesia.co.id"
db = "aeondb"
username = "admin"
password = "pelang123"

# Common endpoint
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(db, username, password, {})

# Object endpoint
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)

# Check if authentication was successful
if uid:    
    print(f"Authenticated as {username} (UID: {uid})")    
    for default_code in default_codes:
        print(default_code)
        search_domain = [[['default_code','=',default_code]]]
        product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', search_domain)
        print(product_ids)
        for product_id in product_ids:
            search_domain = [[['product_id','=', product_id]]]
            product_product_barcode_ids = models.execute_kw(db, uid, password, 'product.product.barcode', 'search', search_domain)
            print(product_product_barcode_ids)
            for product_product_barcode_id in product_product_barcode_ids:
                try:
                    print(product_product_barcode_id)
                    product = models.execute_kw(db, uid, password, 'product.product.barcode', 'read', [product_product_barcode_id])
                    # print(json.loads(product[0])['product_json'])
                    models.execute_kw(db, uid, password, 'product.product.barcode', 'unlink', [product_product_barcode_id])
                except Exception as e:
                    print(e)
else:
    print("Authentication failed.")