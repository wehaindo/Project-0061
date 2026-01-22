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

    
    search_domain = [[['branch_ids','=',41],['to_date','>=','2025-05-19']]]
    # search_domain = [[['to_date','>=','2025-05-19']]]
    pos_promotion_ids = models.execute_kw(db, uid, password, 'pos.promotion', 'search', search_domain)
    print(len(pos_promotion_ids))
    # buy_x_partial_quantity_get_special_price
        
    search_domain = [[['pos_promotion_id','in', pos_promotion_ids],['product_ids','in',product_product_ids]]]
    partial_quantity_fixed_price_ids = models.execute_kw(db, uid, password, 'partial.quantity.fixed.price', 'search', search_domain)
    print(partial_quantity_fixed_price_ids) 
    
    search_domain = [[['id','in',partial_quantity_fixed_price_ids]]]
    partial_quantity_fixed_prices = models.execute_kw(db, uid, password, 'partial.quantity.fixed.price', 'search_read', search_domain)
    for partial_quantity_fixed_price in partial_quantity_fixed_prices:
        print(partial_quantity_fixed_price)

    