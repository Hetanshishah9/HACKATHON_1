from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import os
from key_manager import KeyManager
from encryption import Encryption

app = Flask(__name__)
app.secret_key = b'\x9f\x87\xf3\x18\xb4\x92\xae\x97\xcb\xa1\xeb\xc6\xfc\xf1\x3f\x2b'  # Change this to a securely generated secret key

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

key_manager = KeyManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Generate a unique encryption key for this transaction
            unique_key = key_manager.generate_unique_key()
            print("Unique Encryption Key (raw bytes):", unique_key)  # Print the unique key as bytes
            
            # Encrypt the uploaded file using the unique key
            encryption = Encryption(unique_key, algorithm='aes')
            with open(filepath, 'rb') as f:
                file_data = f.read()
                encrypted_data = encryption.encrypt_data(file_data)

            # Save the encrypted data back to a new location
            encrypted_filepath = os.path.join(UPLOAD_FOLDER, f"encrypted_{filename}")
            with open(encrypted_filepath, 'wb') as ef:
                ef.write(encrypted_data)

            return redirect(url_for('response', unique_key=unique_key.hex()))  # Send hex-encoded key to response

    return render_template('upload.html')

@app.route('/response')
def response():
    unique_key = request.args.get('unique_key')  # Get the unique key from URL parameters
    return render_template('response.html', unique_key=unique_key)

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_file():
    if request.method == 'POST':
        encrypted_filename = request.form['encrypted_filename']  # Get filename from input
        secret_key_input = request.form['secret_key']  # Get secret key from text input

        if not encrypted_filename or not secret_key_input:
            flash('Please provide both encrypted filename and secret key.')
            return redirect(request.url)

        try:
            # Convert the input key from hex to bytes
            secret_key = bytes.fromhex(secret_key_input)

            # Validate the length of the provided key
            if len(secret_key) not in (16, 24, 32):
                flash("Key must be 16, 24, or 32 bytes long.")
                return redirect(request.url)

            # Construct the full path of the encrypted file
            encrypted_filepath = os.path.join(UPLOAD_FOLDER, encrypted_filename)

            # Check if the encrypted file exists
            if not os.path.exists(encrypted_filepath):
                flash("The specified encrypted file does not exist.")
                return redirect(request.url)

            # Decrypt the uploaded encrypted file using the secret key
            encryption = Encryption(secret_key, algorithm='aes')
            
            with open(encrypted_filepath, 'rb') as ef:
                encrypted_data = ef.read()
                try:
                    decrypted_data = encryption.decrypt_data(encrypted_data)
                    decrypted_filename = f"decrypted_{os.path.basename(encrypted_filepath)}"
                    decrypted_filepath = os.path.join(UPLOAD_FOLDER, decrypted_filename)

                    with open(decrypted_filepath, 'wb') as df:
                        df.write(decrypted_data)

                    return send_file(decrypted_filepath, as_attachment=True)  # Send decrypted file for download
                except Exception as e:
                    flash(f"Decryption failed: Invalid key or error during decryption.")
                    return redirect(request.url)
        except Exception as e:
            flash(f"An error occurred: {str(e)}")
            return redirect(request.url)

    return render_template('decrypt.html')

if __name__ == '__main__':
    app.run(debug=True)
