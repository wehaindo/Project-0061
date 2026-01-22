import requests
from requests.auth import HTTPBasicAuth
import simplejson as json
from datetime import datetime, date



def _update_product(product):
    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError ("Type %s not serializable" % type(obj))
    
    products_json = json.dumps(product, default=json_serial)
    return products_json


auth = HTTPBasicAuth('admin','pelang1')
headers = {
    'Content-Type': 'application/json'                  
}                
response = requests.get('https://couchdb.aeonindonesia.co.id/s_7001_products/_design/emtpytaxes/_view/emtpytaxes', auth=auth, headers=headers, verify=False)
if response.status_code == 200:
    json_data = response.json()
    print(json_data['total_rows'])
    if isinstance(json_data, dict):
        couchdb_product = json_data
    if isinstance(json_data, list):
        couchdb_product = json_data[0]
    print(len(couchdb_product['rows']))
    rows = couchdb_product['rows']
    for row in rows:
        #first_row = rows[0]
        first_row_values = row['value']
        first_row_values['taxes_id'] = [1]
        print(first_row_values)     
        print(first_row_values["_id"])
        product_json = _update_product(first_row_values)
        try:
            response = requests.put(f'https://couchdb.aeonindonesia.co.id/s_7001_products/{first_row_values["_id"]}', auth=auth, headers=headers, data=product_json, verify=False)
            print(response.status_code)
            if response.status_code == 200:        
                pass
            if response.status_code == 201:                    
                json_data = response.json()        
            else:
                pass
        except Exception as e:
            print(e)
