import xmlrpc.client
server_url = 'https://aeondb.server1601.weha-id.com'
database = 'aeondb'
user = 'admin'
password = 'd563579a2a6cd5ba0f28526e69b04de4f9d6c24b'
common_auth = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(server_url))
uid = common_auth.authenticate(database, user, password, {})
print(uid)

data_model = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_url))
try:
    data_model.execute_kw(database,uid,password,'pos.order.file','get_pos_order_upload',[])
except Exception as e:
    print(e)