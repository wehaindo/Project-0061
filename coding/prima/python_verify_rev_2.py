from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import base64

# Assuming strKeyPub contains the PEM formatted public key
# strKeyPub = """-----BEGIN PUBLIC KEY-----
# <your-public-key-here>
# -----END PUBLIC KEY-----"""

# strKeyPub = open("998224042354469.pub").read()

strKeyPub = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0mmFaptjE8AxQgwFu3W8
KKQE7byp/Bcs2sSweKOvy7weexj8NtEeGLBREvEUusQ+nTBr8cCLHPE+kL+a2jt7
LqeHhMOott1xw7EwVkikDGcBoH7hpdQsOekrIFaZzvus587s7mBkPO6/b2oQYidA
fGxO1bhT1B0+DUwOoaA4hCBf1kCSg46p7qTYdZsvNPs2epPug9rugcpBTFSdonGC
3IKkhWGaLIH01FuK/Lpqlx8aYlHuk0OIfIHn4b/h5+SmtbMqm7z6CNo3tCz5YwEm
CQ5QVpJ5SsxpNPM/KBvg+6djDpviDzqFpQoPLd2r4tw90npLrcdBmqtEscjsmyeW
EwIDAQAB
-----END PUBLIC KEY-----
"""

# Load the public key
#  public_key = serialization.load_pem_public_key(strKeyPub.encode('utf-8'))
public_key = serialization.load_pem_public_key(strKeyPub.encode('utf-8'))

# Data and signature
string_to_sign = "POST:/v1.0/qr/qr-mpm-notify:1ea66591a4aa555d5d6cf16b0c287f46c5643ffc671b21280c7417ef10ea014a:2024-07-31T15:01:38+07:00"
x_signature = "chqJipL254ceVfAvrMTzRCuEE2W7FziFMCJIPJ7tTf/v8NNmyZR5PtoQ5svKTdLcTPuiIzNE2tmM2/Mjkbboy/CIUZipE3JyV26DbNabNRtr38K+HoilMr5Cu+NlcDClWrkuQUJHkLSQRkPKe2rRehGVJW9bYAAFJoSZq/PyXaaFT37nQo9Idzl3gRkAO1RxQ5i+qKJkZhfhRN0pkVDPMa1Df/ti1O9sGR1JAOkpILZUNNADsULsEWFmz0npwakrnRJq85VnU2E0VINdDhK7yDtOiMfpG/Ie8xlCPAxL8QfGYNJjE51LrW9t9YAfuh+h2T1ZI45E3RWcZexjvrNoAA=="

# Decode the base64-encoded signature
decoded_signature = base64.b64decode(x_signature)

try:
    # Verify the signature
    public_key.verify(
        decoded_signature,
        string_to_sign.encode('utf-8'),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    is_verified = True
except InvalidSignature:
    is_verified = False

print("Signature is verified:", is_verified)
