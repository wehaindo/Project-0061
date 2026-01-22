import sys

from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from base64 import b64decode,b64encode
import json


message =  "POST:/v1.0/qr/qr-mpm-notify:1ea66591a4aa555d5d6cf16b0c287f46c5643ffc671b21280c7417ef10ea014a:2024-07-31T15:01:38+07:00"
digest = SHA256.new()
digest.update(message.encode('utf-8'))

sig = 'bedc06f6b6cb0edc5c426ec7bb4aad32fbba4efe239e71804047bc0eca3081475641563250092528521879df93ca22474926ecc4baeec98aaf90dffe465ef384917ecf41fbbc332033561f40f13d130d540f9d95114c3b12f05b90351580860453876d4fa30dd6f94a96a92f9684015ccd806c7a053ebf07861091a35d057201'
sig = bytes.fromhex(sig)  # convert string to bytes object

# file_content = open("998224042354469.pub").read()
# file_content.replace("-----BEGIN PUBLIC KEY-----", "")
# file_content.replace("-----END PUBLIC KEY-----", "")
# file_content.replace("\n", "")
# file_content.replace("\r", "")
file_content = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0mmFaptjE8AxQgwFu3W8KKQE7byp/Bcs2sSweKOvy7weexj8NtEeGLBREvEUusQ+nTBr8cCLHPE+kL+a2jt7LqeHhMOott1xw7EwVkikDGcBoH7hpdQsOekrIFaZzvus587s7mBkPO6/b2oQYidAfGxO1bhT1B0+DUwOoaA4hCBf1kCSg46p7qTYdZsvNPs2epPug9rugcpBTFSdonGC3IKkhWGaLIH01FuK/Lpqlx8aYlHuk0OIfIHn4b/h5+SmtbMqm7z6CNo3tCz5YwEmCQ5QVpJ5SsxpNPM/KBvg+6djDpviDzqFpQoPLd2r4tw90npLrcdBmqtEscjsmyeWEwIDAQAB"
print(file_content)
public_key = RSA.importKey(file_content)

verifier = PKCS1_v1_5.new(public_key)
verified = verifier.verify(digest, sig)

if verified:
    print('Successfully verified message')
else:
    print('FAILED')