# Source: Geeks for Geeks. https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/.

from cryptography.fernet import Fernet

encryption_key = Fernet.generate_key()

fernet = Fernet(encryption_key)