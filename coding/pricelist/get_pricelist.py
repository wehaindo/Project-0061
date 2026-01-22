import xmlrpc.client
import random  
import string  


# print(access_tokens)
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
    
    product_sku_ids = []    
    with open('product_sku.txt', 'r') as file:
        # Read each line in the file
        for line in file:
            # Print each line
            product_sku_ids.append(line.replace('\n', ''))
                
    search_domain = [[['default_code','in', product_sku_ids]]]    
    # search_domain = [[['default_code','=', product_sku_id]]]    
    # print(search_domain)
    product_product_ids = models.execute_kw(db, uid, password, 'product.product', 'search', search_domain)
    print(len(product_product_ids))

    
    # search_domain = [[['branch_ids','=',41],['to_date','>=','2025-05-19']]]
    search_domain = [[['branch_id','=',41],['date_end','>=','2025-05-19'],['product_id','in',product_product_ids]]]
    product_pricelist_item_ids = models.execute_kw(db, uid, password, 'product.pricelist.item', 'search_read', search_domain)
    # print(product_pricelist_item_ids)
    print(len(product_pricelist_item_ids))
    row = 0
    for product_pricelist_item_id in product_pricelist_item_ids:
        row = row + 1
        print(row, '\n')
        
    
    