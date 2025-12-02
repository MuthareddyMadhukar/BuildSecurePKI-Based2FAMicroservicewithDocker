import subprocess
import base64
import sys

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

STUDENT_PRIVATE_KEY_PATH = "student_private.pem"
INSTRUCTOR_PUBLIC_KEY_PATH = "instructor_public.pem"


def debug_print(msg: str):
    print(msg)
    sys.stdout.flush()


def get_latest_commit_hash() -> str:
    debug_print("[1] Getting latest commit hash...")
    commit_hash = subprocess.check_output(
        ["git", "log", "-1", "--format=%H"],
        encoding="utf-8"
    ).strip()
    debug_print(f"[1] Commit hash: {commit_hash}")
    return commit_hash


def load_student_private_key():
    debug_print("[2] Loading student_private.pem...")
    with open(STUDENT_PRIVATE_KEY_PATH, "rb") as f:
        key_data = f.read()
    private_key = serialization.load_pem_private_key(
        key_data,
        password=None,
    )
    debug_print("[2] Loaded student private key.")
    return private_key


def load_instructor_public_key():
    debug_print("[3] Loading instructor_public.pem...")
    with open(INSTRUCTOR_PUBLIC_KEY_PATH, "rb") as f:
        key_data = f.read()
    public_key = serialization.load_pem_public_key(
        key_data
    )
    debug_print("[3] Loaded instructor public key.")
    return public_key


def sign_message(message: str, private_key) -> bytes:
    debug_print("[4] Signing commit hash with RSA-PSS-SHA256...")
    message_bytes = message.encode("utf-8")

    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    debug_print(f"[4] Signature length: {len(signature)} bytes")
    return signature


def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    debug_print("[5] Encrypting signature with instructor public key (RSA/OAEP-SHA256)...")
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    debug_print(f"[5] Ciphertext length: {len(ciphertext)} bytes")
    return ciphertext


def main():
    debug_print("=== Commit Proof Generation Started ===")

    # 1. Get commit hash
    commit_hash = get_latest_commit_hash()

    # 2. Load student private key
    student_priv = load_student_private_key()

    # 3. Sign commit hash (ASCII string)
    signature = sign_message(commit_hash, student_priv)

    # 4. Load instructor public key
    instructor_pub = load_instructor_public_key()

    # 5. Encrypt signature with instructor public key
    encrypted_signature = encrypt_with_public_key(signature, instructor_pub)

    # 6. Base64 encode encrypted signature
    encrypted_signature_b64 = base64.b64encode(encrypted_signature).decode("utf-8")

    debug_print("=== OUTPUT ===")
    print("Commit Hash:")
    print(commit_hash)
    print("\nEncrypted Signature (Base64):")
    print(encrypted_signature_b64)
    debug_print("=== Done ===")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Print any error so we can see what went wrong
        print("ERROR:", repr(e))
        sys.exit(1)
