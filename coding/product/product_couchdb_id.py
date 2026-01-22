import xmlrpc.client
import random  
import string  



def specific_string(length):  
    sample_string = 'pqrstuvwxy' # define the specific string  
    # define the condition for random string  
    result = ''.join((random.choice(sample_string)) for x in range(length))  
    print(" Randomly generated string is: ", result)
    return result

product_ids = []
# Open the file in read mode
with open('productsid.txt', 'r') as file:
    # Read each line in the file
    for line in file:
        # Print each line
        product_ids.append(int(line.replace('\n', '')))

print(product_ids)
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
    search_domain = [[['id','in',product_ids],['active','=', True]]]   
    print(search_domain)     
    product_template_ids = models.execute_kw(db, uid, password, 'product.template', 'search_read', search_domain)                        
    print(len(product_template_ids))
else:
    print("Authentication failed.")