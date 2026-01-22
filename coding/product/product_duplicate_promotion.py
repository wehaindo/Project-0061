import xmlrpc.client
import random  
import string  

def specific_string(length):  
    sample_string = 'pqrstuvwxy' # define the specific string  
    # define the condition for random string  
    result = ''.join((random.choice(sample_string)) for x in range(length))  
    print(" Randomly generated string is: ", result)
    return result

default_codes = []
# Open the file in read mode
with open('productsku.txt', 'r') as file:
    # Read each line in the file
    for line in file:
        # Print each line
        default_codes.append(line.replace('\n', ''))

print(default_codes)
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
        search_domain = [[['default_code','=',default_code]]]
        print(search_domain)
        product_ids = models.execute_kw(db, uid, password, 'product.template', 'search', search_domain)        
        # print(product_ids)
        print("-->")
        for product_id in product_ids:
            print(product_id)            
            # Pricelist Item
            search_domain = [[['product_tmpl_id','=', product_id]]]
            product_pricelist_item_ids = models.execute_kw(db, uid, password, 'product.pricelist.item', 'search', search_domain)        
            print("---->")
            if len(product_pricelist_item_ids) == 0:
                print("No Pricelist Item") 
            for product_pricelist_item_id in product_pricelist_item_ids:
                print("--",product_pricelist_item_id)
            print("<----")            
            #Partial Promo
            #Partial Quantity Fixed Price
            search_domain = [[['product_tmpl_id','=', product_id]]]
            product_product_ids = models.execute_kw(db, uid, password, 'product.product', 'search', search_domain)                    
            if len(product_product_ids) > 0:                
                product_product_id = product_product_ids[0]                
                search_domain = [[['product_ids', 'in' , [product_product_id]]]]
                partial_quantity_fixed_price_ids = models.execute_kw(db, uid, password, 'partial.quantity.fixed.price', 'search', search_domain)        
                if len(partial_quantity_fixed_price_ids) == 0:
                    print("No Partial")
                else:
                    print(partial_quantity_fixed_price_ids)                        
            #Combination Promo
            
        #     product_product_barcode_ids = models.execute_kw(db, uid, password, 'product.product.barcode', 'search', search_domain)
        #     print(product_product_barcode_ids)
        #     for product_product_barcode_id in product_product_barcode_ids:
        #         try:
        #             models.execute_kw(db, uid, password, 'product.product.barcode', 'unlink', [product_product_barcode_id])
        #         except Exception as e:
        #             print(e)
        print("<--")
else:
    print("Authentication failed.")