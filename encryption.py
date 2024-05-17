from cryptography.fernet import Fernet
import json, base64, os

def encryption(data, notkey_path, file_path):

    # Generate a random key
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)

    # os.environ["Fernet_key"] = str(key)

    # use environment variable instead of key.bin 
    with open(notkey_path, "wb") as file:
        file.write(key)

    # Your JSON data
    data = data

    # Convert data to JSON string
    json_data = json.dumps(data)

    # Encrypt the JSON string
    cipher_text = cipher_suite.encrypt(json_data.encode())

    # Write encrypted data to a file
    with open(file_path, "wb") as file:
        file.write(cipher_text)

def decryption(notkey_path, file_path):
    # key = os.getenv("Fernet_key")
    # print(key)

    with open(notkey_path, "rb") as file:
        key=file.read()
        cipher_suite = Fernet(key)

    # Read the encrypted data from the file
    with open(file_path, "rb") as file:
        encrypted_data = file.read()

    # Decrypt the data
    decrypted_data = cipher_suite.decrypt(encrypted_data)

    # Decode the bytes and load JSON
    json_data = json.loads(decrypted_data.decode())

    return json_data

