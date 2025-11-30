import requests
import json

def request_seed(student_id: str, github_repo_url: str, api_url: str):
    with open("student_public.pem", "r") as f:
        public_key = f.read().strip()

    # ❌ DO NOT do .replace("\n", "\\n")
    # Let requests/json handle the newlines.
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                encrypted_seed = data.get("encrypted_seed")
                with open("encrypted_seed.txt", "w") as f:
                    f.write(encrypted_seed)
                print("✅ Encrypted seed saved to encrypted_seed.txt")
            else:
                print("❌ API Error:", data)
        else:
            print("❌ HTTP Error:", response.status_code, response.text)

    except requests.exceptions.RequestException as e:
        print("⚠️ Request failed:", e)


if __name__ == "__main__":
    STUDENT_ID = "23A91A61A2"  # put your real ID
    GITHUB_REPO_URL = "https://github.com/MuthareddyMadhukar/BuildSecurePKI-Based2FAMicroservicewithDocker"
    API_URL = "https://eajeyq4r3zljoq4rpovy2nthda0vtjqf.lambda-url.ap-south-1.on.aws"

    request_seed(STUDENT_ID, GITHUB_REPO_URL, API_URL)
