import socket
import logging
from key_manager import KeyManager
from file_handler import FileHandler
from encryption import Encryption
import os

# Configure logging
logging.basicConfig(
    filename='client.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def send_file(client_socket, filename):
    try:
        # Generate a unique encryption key for this transfer
        unique_key = os.urandom(32)  # Generate a new 32-byte key
        logging.info(f"Unique Encryption Key for this transfer: {unique_key.hex()}")
        
        # Print the unique key to the console
        print(f"Unique Encryption Key for this transfer: {unique_key.hex()}")

        # Create a new Encryption instance with the unique key
        encryption = Encryption(unique_key, algorithm='aes')
        file_data = FileHandler.read_file(filename)
        encrypted_file_data = encryption.encrypt_data(file_data)

        # Send both the encrypted data and the unique key to the server
        client_socket.sendall(encrypted_file_data)
        logging.info(f"Sent {filename} successfully.")
        
        encrypted_response = client_socket.recv(1024)
        decrypted_response = encryption.decrypt_data(encrypted_response)
        print("Server Response:", decrypted_response.decode())
    except Exception as e:
        logging.error(f"Error sending file '{filename}': {e}")
        print(e)

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', 12345))
        logging.info("Connected to server.")
        
        while True:
            command = input("Enter command (send/exit): ").strip().lower()
            if command == 'exit':
                break
            elif command == 'send':
                filename = input("Enter the full path of the file to send: ")
                send_file(client_socket, filename)
            else:
                print("Invalid command. Please enter 'send' or 'exit'.")
    except Exception as e:
        logging.error(f"Connection error: {e}")
    finally:
        client_socket.close()
        logging.info("Connection closed.")

if __name__ == "__main__":
    main()