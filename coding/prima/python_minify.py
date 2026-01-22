import json

# Example request body dictionary
request_body = {
    "partnerReferenceNo": "1231231232",
    "merchantId": "998224042354469",
    "terminalId": "601",
    "amount": {
        "value": "15000.00",
        "currency": "IDR"
    },
    "additionalInfo": {
        "productType": "payment pos 601"
    }
}

# Serialize the JSON request body
serialized_request_body = json.dumps(request_body)

# Replace single quotes with double quotes
serialized_request_body = serialized_request_body.replace("'", '"')

# Remove spaces from the serialized request body
minified_request_body = ''.join(serialized_request_body.split())

print(minified_request_body)