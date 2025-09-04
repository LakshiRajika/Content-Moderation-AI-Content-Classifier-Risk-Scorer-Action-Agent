import re
import hashlib
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

class SecurityUtils:
    def __init__(self):
        self.key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher_suite = Fernet(self.key)
    
    def sanitize_input(self, input_text):
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>{}[\]]', '', input_text)
        # Limit length to prevent DoS attacks
        return sanitized[:10000]
    
    def encrypt_data(self, data):
        return self.cipher_suite.encrypt(data.encode())
    
    def decrypt_data(self, encrypted_data):
        return self.cipher_suite.decrypt(encrypted_data).decode()

# Create singleton instance
security_utils = SecurityUtils()

# Helper functions
def sanitize_input(text):
    return security_utils.sanitize_input(text)

def encrypt_data(data):
    return security_utils.encrypt_data(data)

def decrypt_data(encrypted_data):
    return security_utils.decrypt_data(encrypted_data)