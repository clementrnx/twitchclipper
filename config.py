import streamlit as st

st.set_page_config(page_title="Setup", layout="centered")
st.markdown("<style>.stApp { background-color: #0a0a0a; color: #facc15; } .stButton>button { background-color: #facc15 !important; color: #000; font-weight: bold; width: 100%; }</style>", unsafe_allow_html=True)

st.title("Configuration")

with st.form("setup"):
    cid = st.text_input("Client ID", type="password")
    csec = st.text_input("Client Secret", type="password")
    if st.form_submit_button("Sauvegarder"):
        if cid and csec:
            with open(".env", "w") as f:
                f.write(f"TWITCH_CLIENT_ID={cid}\nTWITCH_CLIENT_SECRET={csec}")
            st.success("Configuré.")
