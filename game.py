import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(page_title="🎮 Pollution Runner", layout="wide")
st.title("🌍 Pollution Runner — لعبة التلوث")

# تأكد من وجود الملف
if not os.path.exists("game.html"):
    st.error("⚠️ لم يتم العثور على ملف game.html في نفس المجلد.")
else:
    with open("game.html", "r", encoding="utf-8") as f:
        html_code = f.read()

    components.html(html_code, height=600, scrolling=False)
