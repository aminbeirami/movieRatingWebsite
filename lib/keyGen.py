from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import random
import string
import base64

class RSAEncryption():

	def generate_keys(self):
		random_generator = Random.new().read
		key = RSA.generate(1024,random_generator)
		privateKey = key.exportKey()
		publicKey = key.publickey().exportKey()
		return publicKey, privateKey

	def encryption(self,message, publicKey):
		publicKeyObject = RSA.importKey(publicKey)
		randomParameter = random.choice(string.ascii_uppercase)
		encryptedMessage = publicKeyObject.encrypt(message.encode('utf-8'),randomParameter)[0]
		encodedEncryptedMessage = base64.b64encode(encryptedMessage)
		return encodedEncryptedMessage

	def decryption(self,encodedMessage, privateKey):
		KeyObject = RSA.importKey(privateKey)
		decodedMessage = base64.b64decode(encodedMessage)
		decryptedMessage = KeyObject.decrypt(decodedMessage)
		return decryptedMessage

	def generate_signature(self, message, privateKey):
		privateKeyObject = RSA.importKey(privateKey)
		hashedMessage = SHA256.new()
		hashedMessage.update(message)
		signer = PKCS1_v1_5.new(privateKeyObject)
		signature = signer.sign(hashedMessage)
		encodedSignature = base64.b64encode(signature)
		return encodedSignature

	def verifying_signature (self, message, signature, publicKey):
		KeyObject = RSA.importKey(publicKey)
		hashedMessage = SHA256.new()
		hashedMessage.update(message)
		decodedSignature = base64.b64decode(signature)
		verifier = PKCS1_v1_5.new(KeyObject)
		autheticate = verifier.verify(hashedMessage,decodedSignature)
		if autheticate:
			return 'Trusted'
		else:
			return 'Untrusted'