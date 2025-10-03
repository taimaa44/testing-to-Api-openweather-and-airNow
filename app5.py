import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import random
import pandas as pd

# =========================
# API Keys
# =========================
AIRNOW_API_KEY = "35B42644-6AAB-4CE1-9DCD-66DED91093FF"
WEATHER_API_KEY = "1b2eb58890b4e4c651d782337a05bee4"

# =========================
# ولايات مع احداثيات
# =========================
states_info = {
    "New York": {"zip": "10001", "lat": 40.7128, "lon": -74.0060},
    "California": {"zip": "90210", "lat": 34.0522, "lon": -118.2437},
    "Texas": {"zip": "73301", "lat": 30.2672, "lon": -97.7431},
    "Florida": {"zip": "33101", "lat": 25.7617, "lon": -80.1918},
    "Illinois": {"zip": "60601", "lat": 41.8781, "lon": -87.6298},
    "Pennsylvania": {"zip": "19019", "lat": 39.9526, "lon": -75.1652},
    "Ohio": {"zip": "44101", "lat": 41.4993, "lon": -81.6944},
    "Georgia": {"zip": "30301", "lat": 33.7490, "lon": -84.3880},
    "North Carolina": {"zip": "27565", "lat": 35.7596, "lon": -79.0193},
}

# =========================
# Functions
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
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            wind = data["wind"]["speed"]
            desc = data["weather"][0]["main"]
            return temp, humidity, wind, desc
    except:
        pass
    return None, None, None, None

# =========================
# Streamlit UI
# =========================
st.title("🌎 Air Quality & Weather Map - USA")

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
trees_df = pd.DataFrame([])

# =========================
# أسوأ ولاية
# =========================
if not df["AQI"].isnull().all():
    worst = df.loc[df["AQI"].idxmax()]
    st.error(f"🚨 أسوأ ولاية: {worst['State']} (AQI={worst['AQI']} - {worst['Category']})")

    num_trees = st.slider("اختر عدد الأشجار 🌳", 10, 100, 30)

    if st.button("🌳 ازرع أشجار"):
        trees = []
        for _ in range(num_trees):
            trees.append({
                "lat": worst["lat"] + random.uniform(-0.5, 0.5),
                "lon": worst["lon"] + random.uniform(-0.5, 0.5),
            })
        trees_df = pd.DataFrame(trees)

# =========================
# خريطة Leaflet
# =========================
m = folium.Map(location=[39, -98], zoom_start=4)

for _, row in df.iterrows():
    if pd.notna(row["AQI"]):
        color = "green"
        if row["AQI"] > 100:
            color = "red"
        elif row["AQI"] > 50:
            color = "orange"

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
            radius=10,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=popup_text
        ).add_to(m)

if not trees_df.empty:
    for _, t in trees_df.iterrows():
        folium.Marker(
            location=[t["lat"], t["lon"]],
            icon=folium.DivIcon(html="🌳")
        ).add_to(m)

st_folium(m, width=900, height=600)

# =========================
# بطاقات الطقس و AQI
# =========================
st.subheader("📋 تفاصيل الطقس وجودة الهواء لكل ولاية")

cols = st.columns(5)
for i, row in enumerate(df.itertuples()):
    col = cols[i % 5]  # 5 بطاقات بالصف
    with col:
        st.markdown(f"""
        <div style='border-radius:15px; padding:15px; margin:5px; background:#f9f9f9; text-align:center;'>
            <h4>{row.State}</h4>
            <p>🌡️ {row.Temp} °C</p>
            <p>💧 {row.Humidity}%</p>
            <p>💨 {row.Wind} km/h</p>
            <p>☁️ {row.Weather}</p>
            <p>🟢 AQI: <b>{row.AQI}</b> ({row.Category})</p>
            <p>🧪 {row.Pollutant}</p>
        </div>
        """, unsafe_allow_html=True)
