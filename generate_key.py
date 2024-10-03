import os

# Generate a random 32-byte key for AES (ensure it's exactly this length)
key = os.urandom(32)

with open("Secret.key", "wb") as key_file:
    key_file.write(key)

print("New AES-compatible key generated and saved to 'Secret.key'.")