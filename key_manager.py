import os
from cryptography.fernet import Fernet

class KeyManager:
    def __init__(self, key_file='Secret.key'):
        self.key_file = key_file
        self.key = self.load_key()

    def generate_unique_key(self):
        """Generate a new unique Fernet key."""
        # Generate a random 32-byte key for AES
        return os.urandom(32)  # Generates a random key of 32 bytes

    def load_key(self):
        """Load the encryption key from a file."""
        if not os.path.exists(self.key_file):
            return self.generate_unique_key()  # Generate a new key if it doesn't exist
        
        # Load the key as bytes
        key = open(self.key_file, 'rb').read()
        
        # Check the length of the key for AES compatibility (max length is 32 bytes)
        if len(key) > 32:
            raise ValueError("Key must be at most 32 bytes long.")
        
        return key  # Return the key as bytes for AES compatibility