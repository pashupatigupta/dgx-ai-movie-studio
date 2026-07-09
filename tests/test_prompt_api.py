import requests
from config.settings import COMFY_URL

response = requests.get(f"{COMFY_URL}/object_info")

print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()
    print(f"Available Nodes: {len(data)}")

    print("\nSample Nodes:")

    for node in list(data.keys())[:15]:
        print("-", node)
else:
    print(response.text)
