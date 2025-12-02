#!/usr/bin/env python3
# Cron script to log 2FA codes every minute

import os
import datetime
import base64
import pyotp

SEED_PATH = "/data/seed.txt"


def hex_to_base32(hex_seed: str) -> str:
    """Convert hex string to base32 string"""
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode("utf-8")


def main():
    try:
        # 1️⃣ Read hex seed
        if not os.path.exists(SEED_PATH):
            print("Seed file not found, skipping...")
            return

        with open(SEED_PATH, "r") as f:
            hex_seed = f.read().strip()

        # 2️⃣ Generate current TOTP code
        base32_seed = hex_to_base32(hex_seed)
        totp = pyotp.TOTP(base32_seed)
        code = totp.now()

        # 3️⃣ Current UTC timestamp
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # 4️⃣ Output formatted line
        print(f"{timestamp} - 2FA Code: {code}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
