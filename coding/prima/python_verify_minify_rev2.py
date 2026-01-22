import hashlib
import binascii
import json

# Input string
string_to_sign = json.dumps({"amount":{"currency":"IDR","value":"6000.00"},"originalReferenceNo":"421315017683","latestTransactionStatus":"00","additionalInfo":{"invoiceNumber":"57906562075790656207","merchantData":{"mpan":"9360099800000004725","merchantId":"998224042354469","terminalId":"AEON0001"},"transactionDate":"2024-07-31T15:01:23+07:00","transactionHash":"48654303201AF137B8284A72026595E7C1B106FDE8AA2E5D89F290DF391283BF","transactionId":"998224042354469.421315017683.0731150123","issuerData":{"cPan":"9360048400000008883","issInsCode":"484","issInsName":"BANK HANA"}},"originalPartnerReferenceNo":"Order 010280008","transactionStatusDesc":"PURCHASE_APPROVED"}, separators=(',', ':'))
print(string_to_sign)

# Compute SHA-256 hash
sha256_hash = hashlib.sha256(string_to_sign.encode('utf-8')).digest()
print(sha256_hash)

# Convert to a BigInteger equivalent (for unsigned behavior)
number = int.from_bytes(sha256_hash, byteorder='big')
print(number)

# Convert the BigInteger to a hexadecimal string
hex_string = format(number, 'x')

# Pad with leading zeros to ensure it has 64 characters
hex_string = hex_string.zfill(64)

print(hex_string)