import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()

HOST = os.getenv("DATABRICKS_HOST")
TOKEN = os.getenv("DATABRICKS_TOKEN")
SPACE_ID = os.getenv("GENIE_SPACE_ID")

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("Step 1: Starting conversation...")
url = f"{HOST}/api/2.0/genie/spaces/{SPACE_ID}/start-conversation"
resp = requests.post(url, headers=headers, json={"content": "how many customers do we have?"})
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")

if resp.status_code == 200:
    data = resp.json()
    conv_id = data.get("conversation_id")
    msg_id = data.get("message_id")
    print(f"\nStep 2: Polling for result...")
    print(f"conversation_id: {conv_id}")
    print(f"message_id: {msg_id}")

    for i in range(10):
        time.sleep(3)
        poll_url = f"{HOST}/api/2.0/genie/spaces/{SPACE_ID}/conversations/{conv_id}/messages/{msg_id}"
        poll_resp = requests.get(poll_url, headers=headers)
        print(f"Poll {i+1} status: {poll_resp.status_code}")
        print(f"Poll {i+1} response: {poll_resp.text[:300]}")
        
        result = poll_resp.json()
        status = result.get("status")
        print(f"Message status: {status}")
        
        if status == "COMPLETED":
            print(f"\nFinal answer: {result}")
            break