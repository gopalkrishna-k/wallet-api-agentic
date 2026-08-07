import threading
import requests

URL = "http://127.0.0.1:8000/wallet/debit"

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozLCJ1c2VybmFtZSI6ImtvbWFsIiwiZXhwIjoxNzg2MTAwNzQ4fQ.4C7mKBYGa61-uOQaPCUVO_rhNKcltma0nJCy7rxkO4Q"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

payload = {
    "amount": 10
}

results = []


def debit():

    response = requests.post(
        URL,
        json=payload,
        headers=headers
    )

    results.append(response.status_code)


threads = []

for _ in range(50):
    thread = threading.Thread(target=debit)
    threads.append(thread)


print("Starting requests...")

for thread in threads:
    thread.start()


for thread in threads:
    thread.join()


success = results.count(200)
failed = len(results) - success

print("\nTest Completed")
print(f"Success : {success}")
print(f"Failed  : {failed}")