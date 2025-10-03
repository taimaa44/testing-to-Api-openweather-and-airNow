import streamlit as st
import requests
import matplotlib.pyplot as plt
from datetime import datetime

# API Key
API_KEY = "1b2eb58890b4e4c651d782337a05bee4"

st.title("🌦️ تطبيق التنبؤ بالطقس")

# إدخال من المستخدم
city = st.text_input("أدخل اسم المدينة:", "New York")

if st.button("جلب البيانات"):
    # رابط forecast (خمسة أيام قادمة)
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ar"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        st.subheader(f"📍 الطقس الحالي والتنبؤ في {city}")

        temps = []
        times = []

        for item in data["list"][:10]:  # أول 10 نتائج (حوالي 30 ساعة قادمة)
            temp = item["main"]["temp"]
            time = datetime.fromtimestamp(item["dt"])
            desc = item["weather"][0]["description"]

            temps.append(temp)
            times.append(time.strftime("%d-%m %H:%M"))

        # عرض جدول مبسط
        st.write("### 🔸 بيانات قادمة:")
        for t, temp in zip(times, temps):
            st.write(f"{t} → {temp}°C")

        # رسم خط بياني
        fig, ax = plt.subplots()
        ax.plot(times, temps, marker="o")
        ax.set_title(f"تغير الحرارة في {city}")
        ax.set_xlabel("الوقت")
        ax.set_ylabel("°C")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    else:
        st.error("⚠️ لم أتمكن من جلب البيانات. تأكد من اسم المدينة.")
