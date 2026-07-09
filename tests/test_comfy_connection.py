import requests

from config.settings import COMFY_URL

r = requests.get(COMFY_URL)

print("Status:", r.status_code)

print("Connected Successfully")