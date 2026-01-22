from odoo import models, fields, api, _  
from odoo.exceptions import UserError, ValidationError
import logging
import couchdb
import random
import string


_logger = logging.getLogger(__name__)


class PosSyncCouchDB(models.Model):
    _name = 'pos.sync.couchdb'

    def get_random_string(self, length):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        print("Random string of length", length, "is:", result_str)
        return result_str
    
    def sync(self):
        couch = couchdb.Server('http://admin:admin123@128.199.175.43:5984')
        db = couch['posorders']
        orders = []
        for row in db.view('_all_docs', include_docs=True, limit=1):
            _logger.info(row['doc'])
            #orders.append(row['doc'])
            data = row['doc']
            data['name'] = self.get_random_string(10)
            self.env['pos.order'].create_from_ui([{'data':data}])
        _logger.info(orders)   
            


        
