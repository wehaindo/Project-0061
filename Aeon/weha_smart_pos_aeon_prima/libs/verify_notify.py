from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
import base64
import hashlib
import binascii
import json
import logging


_logger = logging.getLogger(__name__)


#Development
# str_public_key = """-----BEGIN PUBLIC KEY-----
# MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0mmFaptjE8AxQgwFu3W8
# KKQE7byp/Bcs2sSweKOvy7weexj8NtEeGLBREvEUusQ+nTBr8cCLHPE+kL+a2jt7
# LqeHhMOott1xw7EwVkikDGcBoH7hpdQsOekrIFaZzvus587s7mBkPO6/b2oQYidA
# fGxO1bhT1B0+DUwOoaA4hCBf1kCSg46p7qTYdZsvNPs2epPug9rugcpBTFSdonGC
# 3IKkhWGaLIH01FuK/Lpqlx8aYlHuk0OIfIHn4b/h5+SmtbMqm7z6CNo3tCz5YwEm
# CQ5QVpJ5SsxpNPM/KBvg+6djDpviDzqFpQoPLd2r4tw90npLrcdBmqtEscjsmyeW
# EwIDAQAB
# -----END PUBLIC KEY-----
# """


#Production
str_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxqyPHs9E184SMGyQSf+l
tNefo6r85IMM9qopoA1rLFPRggQNHwLzktfGOe2N0kNwMCv6sixIPyAmdC+QZHdQ
Guxyi2m81DOFbyNd4V49pR6Lk+AZGP14g0FJMgt9d/VM9Di5v0a8BH/iNbxP8c6t
TiQi15w0hetpKXP2QdwVSOHggdIWh6osTL23LAc30z/dqTiZueeunSS3WQXvHxdS
4gmRINwurz0Cw74y/07O4SGa1uDmTrc6m4xb8xm1zHv7+C9RBknfhBLZAGgXgpID
F4T+IkYKC9tUlB1wueDJzlWkHg6gnNn5y5ZVKeT34aKxT0wtAK9nTlgi6rm54GSp
QwIDAQAB
-----END PUBLIC KEY-----
"""


class VerifyPrimaNotify():

    def __init__(self, x_timestamp, x_signature, data):
        self.public_key = serialization.load_pem_public_key(str_public_key.encode('utf-8'))
        # self.string_to_sign = string_to_sign
        self.x_timestamp = x_timestamp
        self.x_signature = x_signature
        self.decoded_signature = base64.b64decode(x_signature)
        self.data = data

    def _minify(self):
        # string_to_sign = json.dumps({"amount":{"currency":"IDR","value":"6000.00"},"originalReferenceNo":"421315017683","latestTransactionStatus":"00","additionalInfo":{"invoiceNumber":"57906562075790656207","merchantData":{"mpan":"9360099800000004725","merchantId":"998224042354469","terminalId":"AEON0001"},"transactionDate":"2024-07-31T15:01:23+07:00","transactionHash":"48654303201AF137B8284A72026595E7C1B106FDE8AA2E5D89F290DF391283BF","transactionId":"998224042354469.421315017683.0731150123","issuerData":{"cPan":"9360048400000008883","issInsCode":"484","issInsName":"BANK HANA"}},"originalPartnerReferenceNo":"Order 010280008","transactionStatusDesc":"PURCHASE_APPROVED"}, separators=(',', ':'))
        _logger.info(self.data)
        string_to_sign = json.dumps(self.data, separators=(',', ':'))
        # Compute SHA-256 hash
        sha256_hash = hashlib.sha256(string_to_sign.encode('utf-8')).digest()        
        # Convert to a BigInteger equivalent (for unsigned behavior)
        number = int.from_bytes(sha256_hash, byteorder='big')        
        # Convert the BigInteger to a hexadecimal string
        hex_string = format(number, 'x')
        # Pad with leading zeros to ensure it has 64 characters
        hex_string = hex_string.zfill(64)
        return hex_string        

    def is_verified(self):
        try:
            # Minify
            hex_string = self._minify()
            _logger.info(hex_string)
            string_to_sign = "POST:/v1.0/qr/qr-mpm-notify:" + hex_string + ":" + self.x_timestamp
            _logger.info(string_to_sign)
            # Verify the signature
            self.public_key.verify(
                self.decoded_signature,
                string_to_sign.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except InvalidSignature:
            return False