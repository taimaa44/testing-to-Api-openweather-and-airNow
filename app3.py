import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import random
import pandas as pd
import json

# =========================
# API Keys
# =========================
AIRNOW_API_KEY = "35B42644-6AAB-4CE1-9DCD-66DED91093FF"
WEATHER_API_KEY = "1b2eb58890b4e4c651d782337a05bee4"

# =========================
# ولايات أمريكا (مختصر: الاسم + إحداثيات + zip)
# =========================
states_info = {
    "Alabama": {"zip": "35004", "lat": 32.806671, "lon": -86.791130},
    "Alaska": {"zip": "99501", "lat": 61.370716, "lon": -152.404419},
    "Arizona": {"zip": "85001", "lat": 33.729759, "lon": -111.431221},
    "Arkansas": {"zip": "71601", "lat": 34.969704, "lon": -92.373123},
    "California": {"zip": "90210", "lat": 36.116203, "lon": -119.681564},
    "Colorado": {"zip": "80014", "lat": 39.059811, "lon": -105.311104},
    "Connecticut": {"zip": "06101", "lat": 41.597782, "lon": -72.755371},
    "Delaware": {"zip": "19901", "lat": 39.318523, "lon": -75.507141},
    "Florida": {"zip": "33101", "lat": 27.766279, "lon": -81.686783},
    "Georgia": {"zip": "30301", "lat": 33.040619, "lon": -83.643074},
    "New York": {"zip": "10001", "lat": 40.7128, "lon": -74.0060},
    "Texas": {"zip": "73301", "lat": 31.054487, "lon": -97.563461},
    "Illinois": {"zip": "60601", "lat": 40.349457, "lon": -88.986137},
    "Pennsylvania": {"zip": "19019", "lat": 41.203323, "lon": -77.194527},
    "Ohio": {"zip": "44101", "lat": 40.388783, "lon": -82.764915},
    "Michigan": {"zip": "48201", "lat": 44.182205, "lon": -84.506836},
    "North Carolina": {"zip": "27565", "lat": 35.782169, "lon": -80.793457},
    # ... يمكنك تكملة باقي الولايات إذا حبيت
}

# =========================
# API functions
# =========================
def get_airnow(zipcode):
    url = "https://www.airnowapi.org/aq/observation/zipCode/current/"
    params = {
        "format": "application/json",
        "zipCode": zipcode,
        "distance": 25,
        "API_KEY": AIRNOW_API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200 and r.json():
            data = r.json()
            best = max(data, key=lambda x: x["AQI"])
            return best["AQI"], best["ParameterName"], best["Category"]["Name"]
    except:
        pass
    return None, None, None

def get_weather(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return (
                data["main"]["temp"],
                data["main"]["humidity"],
                data["wind"]["speed"],
                data["weather"][0]["main"],
            )
    except:
        pass
    return None, None, None, None

# =========================
# جمع البيانات
# =========================
st.title("🌎 USA Air Quality & Weather - Real Time")

rows = []
for state, info in states_info.items():
    aqi, pollutant, category = get_airnow(info["zip"])
    temp, humidity, wind, desc = get_weather(info["lat"], info["lon"])
    rows.append({
        "State": state,
        "lat": info["lat"],
        "lon": info["lon"],
        "AQI": aqi,
        "Category": category,
        "Pollutant": pollutant,
        "Temp": temp,
        "Humidity": humidity,
        "Wind": wind,
        "Weather": desc
    })

df = pd.DataFrame(rows)

# تنظيف AQI
df["AQI"] = pd.to_numeric(df["AQI"], errors="coerce")
df = df.dropna(subset=["AQI"])

# =========================
# أسوأ ولاية
# =========================
trees_df = pd.DataFrame([])
if not df.empty:
    worst = df.loc[df["AQI"].idxmax()]
    st.error(f"🚨 أسوأ ولاية: {worst['State']} (AQI={worst['AQI']} - {worst['Category']})")

    num_trees = st.slider("اختر عدد الأشجار 🌳", 10, 100, 20)
    if st.button("🌳 ازرع أشجار في أسوأ ولاية"):
        trees = []
        for _ in range(num_trees):
            trees.append({
                "lat": worst["lat"] + random.uniform(-0.5, 0.5),
                "lon": worst["lon"] + random.uniform(-0.5, 0.5),
            })
        trees_df = pd.DataFrame(trees)

# =========================
# خريطة Choropleth + نقاط
# =========================
m = folium.Map(location=[39, -98], zoom_start=4)

# choropleth
# GeoJSON US States (نقدر نجيب نسخة جاهزة)
geojson_url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json"
geojson_data = requests.get(geojson_url).json()

folium.Choropleth(
    geo_data=geojson_data,
    data=df,
    columns=["State", "AQI"],
    key_on="feature.id",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Air Quality Index (AQI)",
).add_to(m)

# markers لكل ولاية
for _, row in df.iterrows():
    popup_text = f"""
    <b>{row['State']}</b><br>
    AQI: {row['AQI']} ({row['Category']})<br>
    🌡️ Temp: {row['Temp']} °C<br>
    💧 Humidity: {row['Humidity']} %<br>
    💨 Wind: {row['Wind']} m/s<br>
    ☁️ Weather: {row['Weather']}
    """
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=7,
        color="blue",
        fill=True,
        fill_opacity=0.6,
        popup=popup_text
    ).add_to(m)

# الأشجار 🌳
if not trees_df.empty:
    for _, t in trees_df.iterrows():
        folium.Marker(
            location=[t["lat"], t["lon"]],
            icon=folium.DivIcon(html="🌳")
        ).add_to(m)

st.subheader("🗺️ خريطة جودة الهواء")
st_folium(m, width=1000, height=600)

# =========================
# جدول بسيط للولايات
# =========================
st.subheader("📊 بيانات الولايات")
st.dataframe(df)
