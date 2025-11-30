import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP
    
    Args:
        encrypted_seed_b64: Base64-encoded ciphertext
        private_key: RSA private key object
    
    Returns:
        Decrypted hex seed (64-character string)
    """

    # 1. Base64 decode the encrypted seed string
    ciphertext = base64.b64decode(encrypted_seed_b64)

    # 2. RSA/OAEP decrypt with SHA-256
    plaintext_bytes = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    # 3. Decode bytes to UTF-8 string
    seed_hex = plaintext_bytes.decode("utf-8").strip()

    # 4. Validate: must be 64-character hex string
    if len(seed_hex) != 64:
        raise ValueError(f"Invalid seed length: expected 64, got {len(seed_hex)}")

    valid_hex_chars = set("0123456789abcdef")
    if not all(c in valid_hex_chars for c in seed_hex):
        raise ValueError("Seed contains non-hex characters")

    # 5. Return hex seed
    return seed_hex

import os


def load_private_key(path: str = "student_private.pem"):
    with open(path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )
    return private_key


def main():
    # Read encrypted seed (from previous step)
    with open("encrypted_seed.txt", "r") as f:
        encrypted_seed_b64 = f.read().strip()

    # Load private key
    private_key = load_private_key("student_private.pem")

    # Decrypt seed
    seed_hex = decrypt_seed(encrypted_seed_b64, private_key)
    print("✅ Decrypted seed:", seed_hex)

    # Ensure /data directory exists (for container)
    data_dir = "/data"
    os.makedirs(data_dir, exist_ok=True)

    # Store seed at /data/seed.txt
    seed_path = os.path.join(data_dir, "seed.txt")
    with open(seed_path, "w") as f:
        f.write(seed_hex + "\n")

    print(f"✅ Seed written to {seed_path}")


if __name__ == "__main__":
    main()

