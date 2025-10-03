import requests

url = "https://www.airnowapi.org/aq/observation/zipCode/current/"
params = {
    "format": "application/json",
    "zipCode": "10001",   # نيويورك
    "distance": 25,
    "API_KEY": "35B42644-6AAB-4CE1-9DCD-66DED91093FF"
}

r = requests.get(url, params=params)
data = r.json()
print(data)

