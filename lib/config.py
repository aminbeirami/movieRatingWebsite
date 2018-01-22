#Written By Amin Beirami
import os
#POSTGRESQL configuration

SERVER = '127.0.0.1'
USERNAME = "postgres"
PASSWORD = "amin123"
DATABASE = "movierating"

#SecretKey is used to encrypt the session cookies

SECRET_KEY = os.urandom(24)