import os
import requests

KEY = os.environ["KEY"]

url = "https://api.estuary.tech/content/list"

header = {"Authorization": f"Bearer {KEY}"}

query = requests.get(url, headers=header)

print(query.content)
