from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

class Encryption:
    def __init__(self, key, algorithm='fernet'):
        self.algorithm = algorithm
        
        # Ensure the key is appropriate for AES
        if self.algorithm == 'aes':
            if len(key) < 16:
                raise ValueError("Key must be at least 16 bytes long.")
            elif len(key) > 32:
                raise ValueError("Key must be at most 32 bytes long.")
            self.key = key.ljust(32)[:32]  # Pad or truncate to 32 bytes
            
        else:
            self.key = key
            
        if self.algorithm == 'fernet':
            from cryptography.fernet import Fernet
            self.cipher = Fernet(key)

    def encrypt_data(self, data):
        """Encrypt data using the specified algorithm."""
        if self.algorithm == 'fernet':
            return self.cipher.encrypt(data)
        
        elif self.algorithm == 'aes':
            iv = os.urandom(16)  # Generate a random IV
            
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            return iv + encryptor.update(padded_data) + encryptor.finalize()

    def decrypt_data(self, encrypted_data):
        """Decrypt data using the specified algorithm."""
        if self.algorithm == 'fernet':
            return self.cipher.decrypt(encrypted_data)
        
        elif self.algorithm == 'aes':
            iv = encrypted_data[:16]  # Extract IV from the beginning
            
            cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            padded_data = decryptor.update(encrypted_data[16:]) + decryptor.finalize()
            
            return unpadder.update(padded_data) + unpadder.finalize()