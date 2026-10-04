import requests
import json

url = "https://api.gdeltproject.org/api/v2/doc/doc"

params = {
    "query": '"Niger" -Nigeria -"Niger Delta"',
    "mode": "ArtList",
    "maxrecords": 10,
    "format": "json"
}

response = requests.get(url, params=params)

print("Sahel Intelligence - GDELT Collector")
print(response.status_code)

if response.status_code == 200:
    data = response.json()

    with open("data/raw/gdelt_niger.json", "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    for article in data["articles"]:
        print(article["title"])
else:
    print("Error al consultar GDELT:", response.status_code)
