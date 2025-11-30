import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from totp_utils import verify_totp_code

app = FastAPI()

SEED_PATH = "/data/seed.txt"


class Verify2FARequest(BaseModel):
    code: str | None = None


def seed_exists() -> bool:
    return os.path.exists(SEED_PATH)


def read_seed() -> str:
    with open(SEED_PATH, "r") as f:
        return f.read().strip()


@app.post("/verify-2fa")
def verify_2fa(body: Verify2FARequest):
    # 1. Validate code is provided
    if not body.code:
        return JSONResponse(
            status_code=400,
            content={"error": "Missing code"},
        )

    # 2. Check if /data/seed.txt exists
    if not seed_exists():
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )

    try:
        # 3. Read hex seed from file
        hex_seed = read_seed()

        # 4. Verify TOTP code with ±1 period tolerance (valid_window=1)
        is_valid = verify_totp_code(hex_seed, body.code, valid_window=1)

        # 5. Return {"valid": true/false}
        return {"valid": bool(is_valid)}

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Seed not decrypted yet"},
        )
