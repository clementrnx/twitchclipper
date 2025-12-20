import streamlit as st
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
ID = os.getenv('TWITCH_CLIENT_ID')
SEC = os.getenv('TWITCH_CLIENT_SECRET')

def get_token():
    r = requests.post("https://id.twitch.tv/oauth2/token", params={"client_id": ID, "client_secret": SEC, "grant_type": "client_credentials"})
    return r.json().get("access_token")

st.set_page_config(page_title="Downloader", layout="wide")
st.markdown("<style>.stApp { background-color: #0a0a0a; color: #facc15; } .stButton>button { background-color: #facc15 !important; color: #000; font-weight: bold; width: 100%; } .stSelectbox div, .stNumberInput input, .stSlider div { color: white !important; }</style>", unsafe_allow_html=True)

st.title("Twitch Downloader")

if not ID or not SEC:
    st.error("Lancer config.py d'abord.")
    st.stop()

c1, c2 = st.columns(2)
with c1:
    langs = {"Fr": "fr", "En": "en", "Es": "es", "De": "de", "Pt": "pt", "Jp": "ja", "Kr": "ko", "Ru": "ru", "Ar": "ar"}
    lang = langs[st.selectbox("Langue", list(langs.keys()))]
    limit = st.slider("Chaînes", 1, 100, 20)
with c2:
    min_v = st.number_input("Vues min", min_value=0, value=100)
    run = st.button("Lancer")

if run:
    tk = get_token()
    if tk:
        h = {"Client-ID": ID, "Authorization": f"Bearer {tk}"}
        sts = requests.get(f"https://api.twitch.tv/helix/streams?language={lang}&first={limit}", headers=h).json().get('data', [])
        
        if sts:
            pb = st.progress(0)
            for i, s in enumerate(sts):
                uid, name = s['user_id'], s['user_name']
                t = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
                cls = requests.get(f"https://api.twitch.tv/helix/clips?broadcaster_id={uid}&started_at={t}&first=50", headers=h).json().get('data', [])
                v_cls = [c for c in cls if c['view_count'] >= min_v]
                
                if v_cls:
                    path = f"downloads/{name}"
                    os.makedirs(path, exist_ok=True)
                    for cl in v_cls:
                        fname = "".join([c for c in cl['title'] if c.isalnum() or c==' ']).strip()
                        url = cl['thumbnail_url'].split("-preview")[0] + ".mp4"
                        fpath = f"{path}/{fname}.mp4"
                        if not os.path.exists(fpath):
                            with open(fpath, 'wb') as f:
                                for ch in requests.get(url, stream=True).iter_content(1024): f.write(ch)
                pb.progress((i + 1) / len(sts))
            st.success("Fini.")
