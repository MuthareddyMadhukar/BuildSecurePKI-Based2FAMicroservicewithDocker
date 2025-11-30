import base64
import pyotp


def _hex_seed_to_base32(hex_seed: str) -> str:
    """
    Convert 64-char hex seed to base32 string for TOTP
    """
    # 1. hex -> bytes
    seed_bytes = bytes.fromhex(hex_seed)

    # 2. bytes -> base32 (returns bytes)
    base32_bytes = base64.b32encode(seed_bytes)

    # 3. bytes -> str
    return base32_bytes.decode("utf-8")


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed

    Args:
        hex_seed: 64-character hex string

    Returns:
        6-digit TOTP code as string
    """
    # 1 & 2. Convert hex seed to base32
    base32_seed = _hex_seed_to_base32(hex_seed)

    # 3. Create TOTP object (default: SHA-1, 30s, 6 digits)
    totp = pyotp.TOTP(base32_seed)

    # 4. Generate current TOTP
    code = totp.now()  # returns a 6-digit string like "123456"

    # 5. Return code
    return code


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with time window tolerance

    Args:
        hex_seed: 64-character hex string
        code: 6-digit code to verify
        valid_window: Number of periods before/after to accept (default 1 = ±30s)

    Returns:
        True if code is valid, False otherwise
    """
    # 1. Convert hex seed to base32
    base32_seed = _hex_seed_to_base32(hex_seed)

    # 2. Create TOTP object
    totp = pyotp.TOTP(base32_seed)

    # 3. Verify with time window tolerance
    # valid_window=1 means current 30s window ±1 step (so ~±30s)
    is_valid = totp.verify(code, valid_window=valid_window)

    # 4. Return result
    return is_valid

if __name__ == "__main__":
    # Read your decrypted seed from /data/seed.txt or local path
    try:
        with open("/data/seed.txt", "r") as f:
            hex_seed = f.read().strip()
    except FileNotFoundError:
        with open("data/seed.txt", "r") as f:
            hex_seed = f.read().strip()

    code = generate_totp_code(hex_seed)
    print("Current TOTP code:", code)

    is_valid = verify_totp_code(hex_seed, code)
    print("Verification result:", is_valid)
