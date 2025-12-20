import streamlit as st
import requests
import os
import streamlink
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
ID = os.getenv('TWITCH_CLIENT_ID')
SEC = os.getenv('TWITCH_CLIENT_SECRET')

def get_token():
    r = requests.post("https://id.twitch.tv/oauth2/token", params={"client_id": ID, "client_secret": SEC, "grant_type": "client_credentials"})
    return r.json().get("access_token")

st.set_page_config(page_title="Downloader", layout="wide")
st.markdown("<style>.stApp { background-color: #0a0a0a; color: #facc15; } .stButton>button { background-color: #facc15 !important; color: #000; font-weight: bold; width: 100%; }</style>", unsafe_allow_html=True)

st.title("Twitch Top Downloader")

if not ID or not SEC:
    st.error("Lancer config.py d'abord.")
    st.stop()

c1, c2 = st.columns(2)
with c1:
    langs = {"Fr": "fr", "En": "en", "Es": "es", "De": "de", "Pt": "pt", "Jp": "ja", "Kr": "ko", "Ru": "ru", "Ar": "ar"}
    lang = langs[st.selectbox("Langue", list(langs.keys()))]
    target_count = st.slider("Nombre de chaînes", 1, 100, 20)
with c2:
    min_v = st.number_input("Vues min", min_value=0, value=100)
    run = st.button("Lancer")

if run:
    tk = get_token()
    if tk:
        h = {"Client-ID": ID, "Authorization": f"Bearer {tk}"}
        found_channels = {}
        
        st.info("Recherche des chaînes populaires (Live + Replays)...")
        
        # 1. On check d'abord les Lives
        r_live = requests.get(f"https://api.twitch.tv/helix/streams?language={lang}&first=100", headers=h).json().get('data', [])
        for s in r_live:
            if len(found_channels) >= target_count: break
            found_channels[s['user_id']] = s['user_name']

        # 2. Si pas assez, on check les vidéos populaires des dernières 24h
        if len(found_channels) < target_count:
            r_vid = requests.get(f"https://api.twitch.tv/helix/videos?language={lang}&sort=views&period=day&first=100", headers=h).json().get('data', [])
            for v in r_vid:
                if len(found_channels) >= target_count: break
                found_channels[v['user_id']] = v['user_name']

        if found_channels:
            pb = st.progress(0)
            for i, (uid, name) in enumerate(found_channels.items()):
                t_limit = (datetime.utcnow() - timedelta(hours=24)).isoformat() + "Z"
                cls = requests.get(f"https://api.twitch.tv/helix/clips?broadcaster_id={uid}&started_at={t_limit}&first=50", headers=h).json().get('data', [])
                
                v_cls = sorted([c for c in cls if c['view_count'] >= min_v], key=lambda x: x['view_count'], reverse=True)
                
                if v_cls:
                    path = f"downloads/{name}"
                    os.makedirs(path, exist_ok=True)
                    for cl in v_cls:
                        fname = "".join([c for c in cl['title'] if c.isalnum() or c==' ']).strip()
                        fpath = f"{path}/{fname}.mp4"
                        if not os.path.exists(fpath):
                            try:
                                session = streamlink.Streamlink()
                                streams = session.streams(cl['url'])
                                if 'best' in streams:
                                    with open(fpath, 'wb') as f:
                                        for ch in requests.get(streams['best'].url, stream=True).iter_content(1024*1024):
                                            f.write(ch)
                            except: continue
                pb.progress((i + 1) / len(found_channels))
            st.success(f"Fini. {len(found_channels)} chaînes traitées.")
