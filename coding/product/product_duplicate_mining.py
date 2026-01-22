import xmlrpc.client
import random  
import string  


def has_partial_promotion(models, db, uid, password, product_id):
    search_domain = [[['product_tmpl_id','=', product_id]]]
    product_product_ids = models.execute_kw(db, uid, password, 'product.product', 'search', search_domain)                    
    if len(product_product_ids) > 0:                
        product_product_id = product_product_ids[0]                
        search_domain = [[['product_ids', 'in' , [product_product_id]]]]
        partial_quantity_fixed_price_ids = models.execute_kw(db, uid, password, 'partial.quantity.fixed.price', 'search_read', search_domain)        
        if len(partial_quantity_fixed_price_ids) == 0:
            return False
        else:
            # print(partial_quantity_fixed_price_ids) 
            return partial_quantity_fixed_price_ids

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
        # print(search_domain)
        product_ids = models.execute_kw(db, uid, password, 'product.template', 'search_read', search_domain)        
        # print(product_ids)
        # print("-->")
        for product_id in product_ids:
            # print(product_id['create_date'],product_id['write_date'])
            # print(product_id['qty_available'])
            partial_quantity_fixed_price_ids = has_partial_promotion(models, db, uid, password, product_id['id'])
            #print(has_promotion)
            if not partial_quantity_fixed_price_ids:                
                print(default_code, product_id['id'],product_id['qty_available'], product_id['create_date'], product_id['write_date']) 
            else:     
                to_dates = []           
                for partial_quantity_fixed_price_id in partial_quantity_fixed_price_ids:
                    # print(partial_quantity_fixed_price_id['pos_promotion_id'])
                    pos_promotion_ids = models.execute_kw(db, uid, password, 'pos.promotion', 'read', [partial_quantity_fixed_price_id['pos_promotion_id'][0]])        
                    for pos_promotion_id in pos_promotion_ids:
                        to_dates.append(pos_promotion_id['to_date'])                    
                
                print(default_code, product_id['id'], product_id['qty_available'], product_id['create_date'], product_id['write_date'], to_dates)
            
                        
else:
    print("Authentication failed.")