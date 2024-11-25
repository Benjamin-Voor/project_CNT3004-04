FORMAT = "utf-8" # Hard-coded to prevent circular import

import hashlib
password = "password"
hash = hashlib.new('sha256', password.encode(FORMAT)).hexdigest()
print(hash)

# Fernet did not work, but I'll leave the attempted code here, just in case I change my mind.

# Source: Geeks for Geeks. https://www.geeksforgeeks.org/how-to-encrypt-and-decrypt-strings-in-python/.
# from cryptography.fernet import Fernet
# encryption_key = Fernet.generate_key()
# fernet = Fernet(encryption_key)

