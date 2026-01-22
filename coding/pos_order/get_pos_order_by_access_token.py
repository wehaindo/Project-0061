import xmlrpc.client
import random  
import string  

def specific_string(length):  
    sample_string = 'pqrstuvwxy' # define the specific string  
    # define the condition for random string  
    result = ''.join((random.choice(sample_string)) for x in range(length))  
    print(" Randomly generated string is: ", result)
    return result

access_tokens = []
# Open the file in read mode
with open('access_tokens.txt', 'r') as file:
    # Read each line in the file
    for line in file:
        # Print each line
        access_tokens.append(line.replace('\n', ''))

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
    row = 1
    keep = []
    remove = []
    f = open("sql_delete.txt", "a")
    for access_token in access_tokens:
        search_domain = [[['access_token','=',access_token]]]
        # print(search_domain)
        pos_order_ids = models.execute_kw(db, uid, password, 'pos.order', 'search', search_domain)
        keep.append(pos_order_ids[0])
        remove.append(pos_order_ids[1:])
        print(row, " - " ,pos_order_ids)        
        row = row + 1 
        # for product_id in product_ids:
        #     search_domain = [[['product_id','=', product_id]]]
        #     product_product_barcode_ids = models.execute_kw(db, uid, password, 'product.product.barcode', 'search', search_domain)
        #     print(product_product_barcode_ids)
        #     for product_product_barcode_id in product_product_barcode_ids:
        #         try:
        #             models.execute_kw(db, uid, password, 'product.product.barcode', 'unlink', [product_product_barcode_id])
        #         except Exception as e:
        #             print(e)
    # print(keep)
    # print(remove)
    count = 1
    for rows in remove:
        for line in rows:           
            # print(count)
            # print('delete from pos_payment where pos_order_id=' + str(line) + ';')
            # print('delete from pos_order_line where order_id=' + str(line) + ';')
            # print('delete from pos_order where id=' + str(line) + ';')
            f.write('delete from pos_payment where pos_order_id=' + str(line) + ';\n')
            f.write('delete from pos_order_line where order_id=' + str(line) + ';\n')
            f.write('delete from pos_order where id=' + str(line) + ';\n')

            count = count + 1
    f.close()
else:
    print("Authentication failed.")