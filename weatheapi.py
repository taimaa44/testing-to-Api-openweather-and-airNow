"""
import requests

api_key = ""

url = "https://api.openaq.org/v3/locations"

params = {
    "city": "Amman",
    "limit": 5   # نجيب 5 مواقع فقط للتجربة
}

headers = {
    "X-API-Key": api_key
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

print(data)

import requests

api_key = ""
url = "https://api.openaq.org/v3/countries"

headers = {"X-API-Key": api_key}

resp = requests.get(url, headers=headers)
data = resp.json()

for c in data.get("results", []):
    print(c["code"], "-", c["name"])
"""
import requests
from datetime import datetime

api_key = ""
city = "New York"
url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

response = requests.get(url)
data = response.json()

if response.status_code == 200:
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    timestamp = data["dt"]  # وقت آخر تحديث
    
    # تحويله لوقت محلي (حسب timezone الخاص بالمدينة)
    tz_offset = data["timezone"]  # فرق التوقيت بالثواني
    local_time = datetime.utcfromtimestamp(timestamp + tz_offset)

    print(f"الطقس في {city}:")
    print(f"درجة الحرارة: {temp}°C")
    print(f"الوصف: {desc}")
    print(f"الرطوبة: {humidity}%")
    print(f"سرعة الرياح: {wind} m/s")
    print(f"الوقت المحلي: {local_time}")
else:
    print("خطأ:", data)
