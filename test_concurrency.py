import threading
import requests

URL = "http://127.0.0.1:8000/wallet/debit"

TOKEN = "token"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

payload = {
    "amount": 15
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