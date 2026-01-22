var dbInventory = new PouchDB('inventory');
var dbTransaction = new PouchDB('transaction');
var dbCart = new PouchDB('cart');
var dbCustomer = new PouchDB('customer');
var dbCategory = new PouchDB('category');
var dbUser = new PouchDB('user');

function uuid() {
    var chars = '0123456789abcdef'.split('');

    var uuid = [],
        rnd = Math.random,
        r;
    uuid[8] = uuid[13] = uuid[18] = uuid[23] = '-';
    uuid[14] = '4'; // version 4

    for (var i = 0; i < 36; i++) {
        if (!uuid[i]) {
            r = 0 | rnd() * 16;

            uuid[i] = chars[(i == 19) ? (r & 0x3) | 0x8 : r & 0xf];
        }
    }

    return uuid.join('');
}

function getProducts(){
    dbInventory.allDocs({
        include_docs: true,
        attachments: true
    }).then(function (docs) {
        // handle result
        console.log(docs);
        return docs;
    }).catch(function (err) {
        console.log(err);
        return [];
    });
}
