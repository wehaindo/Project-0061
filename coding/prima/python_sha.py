import json
import hashlib

# Example request body dictionary
request_body = {
    'partnerReferenceNo': '1231231232',
    'merchantId': '998224042354469',
    'terminalId': '601',
    'amount': {
        'value': '15000.00',
        'currency': 'IDR'
    },
    'additionalInfo': {
        'productType': 'payment pos 601'
    }
}

# Serialize the JSON request body with minified formatting
minified_request_body = json.dumps(request_body, separators=(',', ':'))

# Calculate the SHA-256 hash of the minified request body
sha256_hash = hashlib.sha256(minified_request_body.encode()).hexdigest()

print("SHA-256 hash: " +  sha256_hash)