import socket
import logging
from key_manager import KeyManager
from file_handler import FileHandler
from encryption import Encryption

# Configure logging
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def start_server():
    key_manager = KeyManager()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(1)
    
    logging.info("Waiting for connection...")
    conn, addr = server_socket.accept()
    logging.info(f"Connection established with {addr}")

    while True:
        try:
            encrypted_data = conn.recv(1024)
            if not encrypted_data:
                logging.info("No data received; closing connection.")
                break
            
            # Ask for the key in hex format entered by user
            entered_key = input("Enter the encryption key to decrypt the file (in hex format): ")
            try:
                unique_key = bytes.fromhex(entered_key)  # Convert hex string to bytes
                logging.info(f"Unique Encryption Key entered by user: {unique_key.hex()}")

                # Create a new Encryption instance with the entered unique key
                encryption = Encryption(unique_key, algorithm='aes')
                
                # Decrypt the received data using the unique key
                decrypted_data = encryption.decrypt_data(encrypted_data)

                # Write the decrypted data to a file
                FileHandler.write_file("received_file.json", decrypted_data)
                logging.info("File received and decrypted successfully.")

                # Display the content of the received and decrypted file
                file_content = FileHandler.read_file("received_file.json")
                print("Decrypted file content:")
                print(file_content.decode('utf-8'))  # Assuming JSON content is UTF-8 encoded

                # Send an acknowledgment response back to the client
                response = "Acknowledged".encode()
                encrypted_response = encryption.encrypt_data(response)
                conn.sendall(encrypted_response)
            except ValueError:
                print("Invalid key! Data transmission aborted.")
                logging.error("Invalid key entered; data transmission aborted.")
            except Exception as e:
                logging.error(f"Error: {e}")
                break

        except Exception as e:
            logging.error(f"Error during communication: {e}")
            break

    conn.close()
    logging.info("Connection closed.")

if __name__ == "__main__":
    start_server()