import asyncio
import os
import cv2
import json
import numpy as np
import whisper
import requests
import random
import streamlink
import subprocess
from pathlib import Path
from PIL import ImageFont, ImageDraw, Image
import streamlit as st
import edge_tts
from datetime import datetime, timedelta

try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

OUTPUT_DIR = Path("TwitchClipper_Production")
OUTPUT_DIR.mkdir(exist_ok=True)
CONFIG_FILE = Path("config_api.json")

def load_permanent_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"cid": "", "sec": ""}

def save_permanent_config(cid, sec):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"cid": cid, "sec": sec}, f)

saved_config = load_permanent_config()

FEMMES_BASE = ["Lana Rhoades", "Mia Khalifa", "Angela White", "Abella Danger", "Riley Reid", "Dani Daniels", "Brandi Love", "Lisa Ann", "Anissa Kate", "Liza Del Sierra", "Nikita Bellucci", "Kendra Lust", "Adriana Chechik", "Sasha Grey", "Lena Paul", "Eva Elfie", "Mia Melano", "Belle Claire", "Kenzie Reeves", "Nicole Aniston", "Tori Black", "Alexis Texas", "Brooklyn Chase", "Karma Rx", "Vina Sky", "Honey Gold", "Katana Kombat", "Cory Chase", "Janice Griffith", "Gina Valentina", "Polska", "Hélydia", "Ruby Nikara", "Maeva Ghennam", "Aya Nakamura", "Nabilla", "Mimi Mathy", "Ophenya", "Wejdene", "Shay", "Marine El Himer", "Maddy Burciaga", "Victoria Mehault", "Kim K", "Poupette Kenza", "Léna Situations", "Amouranth", "Belle Delphine", "Katsuni", "Tiffany Hopkins", "Lolo Ferrari", "Brigitte Lahaie", "Yasmine la rebeu", "Sonia l'algérienne", "Mélissa la métisse", "Manon Tanti", "Jazz Correia", "Maissane", "Mélanie Orl", "Adixia", "Kamila", "Giuseppa", "Hilona", "Léana Zaoui", "Sarah Fraisou", "Kim Glow", "Astrid Nelsia", "Juju Fitcats", "Zahia Dehar", "Milla Jasmine", "Cindy Sander", "Ève Gilles", "Mélanie Dedigama", "Fidji Ruiz", "Shanna Kress", "Ayem Nour", "Capucine Anav", "Amélie Neten", "Loana", "Océane El Himer", "Jessica Thivenin", "Carla Moreau", "Kelly Vedovelli", "Agathe Auproux", "Iris Mittenaere", "Mia la go d'Abidjan", "La prof d'espagnol", "La maman de ton pote", "La caissière de Lidl", "La reine du shatta", "La go de Marcory", "La barbie d'Algérie", "La panthère du Congo", "La lionne du Maroc", "L'ex de Inoxtag", "Tiboudouboudou", "Kylie Jenner", "Cardi B", "Nicki Minaj", "Ice Spice", "Megan Thee Stallion", "Doja Cat", "Sonia du 93", "Kenza du tieks", "Louna la fitness girl", "Ambre la michto", "Léa la gogo danseuse", "Chloé de la compta", "Mélanie la prof de zumba", "Clara de Dubaï", "Sabrina la rebeu", "Inès la petite beurette", "Fatou la malienne", "Aminata la sénégalaise", "Zahra l'égyptienne", "Leila la tunisienne", "Myriam la libanaise", "Sarra l'italienne", "Elena la russe", "Yuki la japonaise", "Mei la chinoise", "Anita la brésilienne", "Carmen l'espagnole", "Heidi l'allemande", "Kim l'américaine", "Britney la blonde", "Vanessa la cougar", "Corinne la secrétaire", "Chantal la daronne", "Monique la boulangère", "Sandrine de la mairie", "Valérie de la police", "Nathalie l'infirmière", "Julie l'étudiante", "Emma la serveuse", "Jade la mannequin", "Rose la fleuriste", "Lola la stripteaseuse", "Nina la dominatrice", "Eva la libertine", "Louna la coquine", "Sasha la cochonne", "Mia la nympho", "Clara la perverse", "Zoe la chaude", "Mila la baveuse", "Joy la soumise", "Alix la rebelle", "Thaïs l'influenceuse", "Maya la fêtarde", "Tessa la gamine", "Emy la voisine", "Clémence la coincée", "Yasmine la sauvage", "Sonia la folle", "Inès la gamine", "Léa la petite sœur", "Manon la cousine", "Julie la belle-mère", "Camille la prof", "Sonia la directrice", "Maeva la bimbo", "Nabilla la star", "Aya la reine", "Shay la boss", "Wejdene la gamine", "Ophenya la tiktokeuse", "Polska la queen", "Ruby la rappeuse", "Mimi la petite", "Zahia la courtisane", "Clara la légende", "Brigitte l'icône", "Katsuni la furie", "Anissa la déesse", "Liza la tigresse", "Nikita la brute", "Lena la douce", "Mia la starlette", "Eva la chipie", "Tori la démoniaque", "Alexis la géante", "Riley la petite", "Abella la furie", "Angela la patronne", "Kendra la MILF", "Brandi la maman", "Lisa la doyenne"]
ATTR_BASE = ["LE MINOU PAS RASÉ ET BIEN SOMBRE", "LA GROSSE CREVASSE TOUTE HUMIDE", "LE POT D'ÉCHAPPEMENT BIEN DILATÉ", "LA PETITE FENTE QUI DEGOULINE", "L'ÉNORME SERRURE DÉJÀ BIEN FORCÉE", "LA GIGA CAVE TOUTE MOISIE", "L'ABRI-BUS BIEN POILU", "L'ÉNORME GARAGE À ZOUGOU", "LES DEUX ÉNORMES BALLONS BIEN GONFLÉS", "LES PAQUETS DE VIANDE BIEN GRAS", "LE GIGA CUL QUI DÉBORDE DU LEGGING", "LA GROSSE PÊCHE BIEN LARGE", "LE GIGA DERRIÈRE QUI FAIT TREMBLER LE SOL", "LE TUNNEL DE LA LIGNE 13", "L'ÉNORME RÉSERVOIR DE SAUCE BLANCHE", "LA PETITE PORTE DE DERRIÈRE TOUTE CHAUDE", "L'ASPIRATEUR À MATRAQUE", "LA SOURCE DE JUS TOUTE COLLANTE", "L'ÉNORME CRATÈRE DE LUNE", "LA FOUFOUNE BIEN ROUGE", "L'ABICOT TOUT BAVEUX", "LA GROSSE MOSSANCE BIEN GRASSE", "LES DEUX ÉNORMES GIGUES DE POULET", "LE GIGA SANDWICH GREC BIEN SAUÇÉ", "LA PISCINE GONFLABLE TOUTE CHAUDE", "LE TOBOGGAN TOUT MOUILLÉ", "LA GROSSE USINE À BONHEUR", "LE NID TOUT DOUILLET ET HUMIDE", "LA GROSSE AIRE DE JEUX BIEN LARGE", "LE GIGA GARAGE POUR CAMION", "LES DEUX AIRBAGS TOUT MOUPY", "LES DEUX GROSSES MICHES BIEN MOULÉES", "LE DERRIÈRE QUI DÉGUEULE DU SHORT", "LE TROU BIEN CHAUD ET ACCUEILLANT", "LA FONTAINE QUI COULE SANS ARRÊT", "LE VOLCAN PRÊT À TOUT LÂCHER", "LE POT DE NUTELLA TOUT COULANT", "LA GROTTE MAGIQUE ET SOMBRE", "LE REBORD DE FENÊTRE BIEN LARGE", "LE BAC À SABLE BIEN HUMIDE", "LE COULOIR DE MÉTRO BIEN VIDE", "LA BOUCHE D'ÉGOUT TOUTE OUVERTE", "L'ASPIRATEUR À ZOUGOU", "LE RÉSERVOIR TOUT PLEIN", "LA FOSSE COMMUNE ET LARGE", "LE CANAPÉ TOUT MOELLEUX", "LA COUETTE BIEN CHAUDE", "LE MATELAS À EAU TOUT MOU", "LA BAIGNOIRE QUI DÉBORDE", "LE SEAU DE POP-CORN BIEN GRAS", "L'HAMBURGER BIEN COULANT", "LA PIZZA TOUTE CHAUDE", "LE KEBAB SAUCE ALGÉRIENNE", "LE TACOS 3 VIANDES BIEN LOURD", "LE CHURROS BIEN SUCRÉ", "LE BEIGNET TOUT GRAS", "LA CRÊPE AU SUCRE TOUTE CHAUDE", "LA GAUFRE BIEN CHAUDE", "LA GLACE À LA VANILLE", "LE MILKSHAKE QUI DÉBORDE", "LA CRÈME CHANTILLY", "LE YAOURT À LA GRECQUE", "LA MOZZARELLA BIEN BLANCHE", "LE FROMAGE QUI PUE LA MORT", "LA SAUCISSE DANS LE PAIN", "LE HOT-DOG BIEN MOUTARDE", "LE NUGGET TOUT CHAUD", "L'AILE DE POULET BIEN GRASSE", "LE PILON DE POULET BIEN CUIT", "LA CÔTELETTE D'AGNEAU BIEN ROSE", "LE ROASTBEEF TOUT ROUGE", "LA JAMBONNE BIEN ROSE", "LA TERRINE DU TERROIR", "LE SAUCISSON BIEN SEC", "LE CHORIZO QUI PIQUE SA MÈRE", "LE SALAMI BIEN GRAS", "LA MORTADELLE BIEN LARGE"]
ACTIONS_BASE = ["RAMONNE SANS AUCUNE PITIÉ", "DÉFONCE LA PORTE ARRIÈRE DE", "S'OUBLIE TOTALEMENT DANS", "REPEINT L'INTÉRIEUR DE", "DÉBOUCHE AU KÄRCHER", "VIDE TOUTE SA RÉSERVE DANS", "FAIT DISPARAÎTRE SA MATRAQUE DANS", "PONCE COMME UN MALADE", "EXPLOSE LE VERROU DE", "ANNIHILE TOTALEMENT", "PULVÉRISE SANS PRESSION", "ASTIQUE LE FOND DE", "LABOURE AVEC SA GROSSE PIOCHE", "RETOURNE COMPLÈTEMENT", "DÉMONTE VIGOUREUSEMENT", "BADIGEONNE DE SAUCE ALGÉRIENNE", "ARROSE COPINEUSEMENT", "PÈTE LES PLOMBS SUR", "SOULEVE LA JUPE DE", "CASSE LE LIT DE", "BASCULE DANS LA FOLIE SUR", "DÉPOUILLE TOTALEMENT", "PRÉLÈVE LE JUS DE", "NETTOIE AU JET D'EAU", "REPEINT LE PLAFOND DE", "FORCE LE PASSAGE DANS", "EXPLOSE LA SERRURE DE", "PÈTE LA SOUPIÈRE DE", "RETOURNE LA CHARRUE DANS", "LABOURE LE CHAMP DE", "SÈME SA GRAINE DANS", "ARROSE LE JARDIN DE", "TOND LA PELOUSE DE", "NETTOIE LE CARRELAGE DE", "PONCE LE PARQUET DE", "VISSE LE BOULON DANS", "MARTELE SANS PITIÉ", "PERCE LE MUR DE", "CASSE LA PORTE DE", "OUVRE LA FENÊTRE DE"]
LIEUX_BASE = ["DANS LES CHIOTTES DU COURS JULIEN", "AU FIVE DE NANTERRE", "DANS UNE CAVE À ÉVRY", "SUR UN ABRIBUS AU TER-TER", "DANS LE BUREAU DU PATRON", "AU MACDO DE CHÂTELET", "DERRIÈRE UNE CHICHA À DUBAÏ", "DANS LE VESTIAIRE DU PSG", "AU COMMISSARIAT DE ROUBAIX", "DANS LA LOGE DE HANOUNA", "SUR LE TOIT DU MONDE", "DANS LE RER D", "AU RAYON SURGELÉS de LIDL", "DANS UNE CABINE d'ESSAYAGE", "AUX QUARTIERS NORD", "SUR LA PLAGE DU PRADO", "DANS LE JACUZZI DE POLSKA", "AU MILIEU D'UN ROND-POINT", "DANS LA SALLE DES PROFS", "AU CAMPING DES FLOTS BLEUS", "DANS L'AMPHI DE LA FAC", "À LA DÉCHETTERIE", "DANS LE BUS DE l'ÉQUIPE DE FRANCE", "AU FESTIVAL DE CANNES", "SUR LE TAPIS ROUGE", "SUR LE PLATEAU DE TPMP", "DANS LES COULISSES DE QUOTIDIEN", "À LA TOUR EIFFEL", "SUR LES CHAMPS-ÉLYSÉES", "À L'ARC DE TRIOMPHE", "AU SACRÉ-CŒUR", "DANS LE MARAIS", "À BASTILLE", "À RÉPUBLIQUE"]

@st.cache_resource
def load_whisper():
    return whisper.load_model("medium")

def draw_3d_text(frame, text, y, font_size, color=(255, 255, 255)):
    font_path = "C:/Windows/Fonts/impact.ttf" if os.name == 'nt' else "/System/Library/Fonts/Supplemental/Impact.ttf"
    img = Image.fromarray(frame)
    draw = ImageDraw.Draw(img)
    try: font = ImageFont.truetype(font_path, font_size)
    except: font = ImageFont.load_default()
    
    lines = [text[i:i+25] for i in range(0, len(text), 25)]
    current_y = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (frame.shape[1] - (bbox[2] - bbox[0])) // 2
        for i in range(5, 0, -1):
            draw.text((x+i, current_y+i), line, font=font, fill=(0, 0, 0))
        draw.text((x, current_y), line, font=font, fill=color)
        current_y += font_size + 5
    return np.array(img)

async def process_video(clip, titre, idx, status_box):
    try:
        s_url = streamlink.Streamlink().streams(clip['url'])['best'].url
        v_in = f"temp_in_{idx}.mp4"
        with open(v_in, "wb") as f: f.write(requests.get(s_url).content)
        
        v_path = f"temp_v_{idx}.mp3"
        await edge_tts.Communicate(titre, "fr-FR-DeniseNeural", rate="+15%").save(v_path)
        
        info = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', v_path], capture_output=True, text=True)
        v_dur = float(info.stdout) if info.stdout else 3.5
        
        model = load_whisper()
        subs = model.transcribe(v_in, fp16=False)
        cap = cv2.VideoCapture(v_in)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        v_no_a = f"temp_no_a_{idx}.mp4"
        vw = cv2.VideoWriter(v_no_a, cv2.VideoWriter_fourcc(*'mp4v'), fps, (1080, 1920))
        
        f_id = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            t = f_id / fps
            bg = cv2.GaussianBlur(cv2.resize(frame, (1080, 1920)), (45, 45), 0)
            sc = 1080 / frame.shape[1]
            res = cv2.resize(frame, (1080, int(frame.shape[0] * sc)))
            bg[(1920-res.shape[0])//2:(1920-res.shape[0])//2+res.shape[0], :] = res
            
            if t <= v_dur:
                bg = draw_3d_text(bg, titre, 150, 70, color=(255, 215, 0))
            for s in subs['segments']:
                if s['start'] <= t <= s['end']:
                    bg = draw_3d_text(bg, s['text'].strip().upper(), 1550, 60)
            vw.write(bg)
            f_id += 1
        cap.release(); vw.release()
        
        final_out = OUTPUT_DIR / f"CLIP_{idx}_{clip['broadcaster_name']}.mp4"
        cmd = (f'ffmpeg -y -i "{v_no_a}" -i "{v_in}" -i "{v_path}" '
               f'-filter_complex "[1:a][2:a]amix=inputs=2:duration=first[a]" '
               f'-map 0:v -map "[a]" -c:v libx264 -preset superfast -c:a aac "{final_out}"')
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        for f in [v_in, v_path, v_no_a]:
            if os.path.exists(f): os.remove(f)
        return final_out
    except: return None

st.set_page_config(page_title="clementrnxx / studio", layout="wide")

st.markdown("""
    <style>
        :root { --primary: #ffcc00; --bg-dark: #000000; }
        .stApp {
            background: url('https://media.giphy.com/media/VZrfUvQjXaGEQy1RSn/giphy.gif') center/cover no-repeat fixed;
            background-color: var(--bg-dark) !important;
        }
        .stApp::before {
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.85); z-index: -1;
        }
        h1, h2 {
            font-family: 'Inter', sans-serif; font-weight: 900;
            color: var(--primary) !important; text-transform: uppercase;
            letter-spacing: 5px; text-shadow: 0 0 10px rgba(255, 204, 0, 0.5);
        }
        .stButton>button {
            background: rgba(0, 0, 0, 0.5) !important; border: 1px solid var(--primary) !important;
            color: var(--primary) !important; font-weight: 800 !important;
            letter-spacing: 2px !important; text-transform: uppercase;
        }
        .stButton>button:hover {
            background: var(--primary) !important; color: black !important;
            box-shadow: 0 0 20px var(--primary);
        }
    </style>
""", unsafe_allow_html=True)

st.title("clementrnxx / studio")

tab_auth, tab_scan, tab_render = st.tabs(["CONFIG", "ANALYSE BUZZ", "GENERATION"])

if 'clips' not in st.session_state: st.session_state.clips = []

with tab_auth:
    c1, c2 = st.columns(2)
    with c1: cid_in = st.text_input("Client ID", value=saved_config["cid"])
    with c2: sec_in = st.text_input("Client Secret", value=saved_config["sec"], type="password")
    if st.button("SAUVEGARDER"):
        save_permanent_config(cid_in, sec_in)
        st.success("Config OK.")

with tab_scan:
    c1, c2 = st.columns(2)
    with c1: target_game = st.text_input("Jeu Specifique", placeholder="ex: League of Legends")
    with c2: target_streamer = st.text_input("Streamer Specifique", placeholder="ex: amine")
    nb_target = st.slider("Nombre de clips", 1, 50, 10)
    period = st.selectbox("Periode", ["Dernieres 24h", "7 jours", "30 jours"])

    if st.button("SCANNER LE BUZZ"):
        try:
            tk = requests.post("https://id.twitch.tv/oauth2/token", params={"client_id":cid_in, "client_secret":sec_in, "grant_type":"client_credentials"}).json()
            h = {"Client-ID":cid_in, "Authorization": f"Bearer {tk['access_token']}"}
            days = 1 if period == "Dernieres 24h" else (7 if period == "7 jours" else 30)
            date_limit = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
            
            found = []
            with st.status("Recherche..."):
                if target_streamer:
                    u = requests.get(f"https://api.twitch.tv/helix/users?login={target_streamer}", headers=h).json()['data'][0]
                    found = requests.get(f"https://api.twitch.tv/helix/clips?broadcaster_id={u['id']}&first={nb_target}&started_at={date_limit}", headers=h).json().get('data', [])
                elif target_game:
                    g = requests.get(f"https://api.twitch.tv/helix/games?name={target_game}", headers=h).json()['data'][0]
                    found = requests.get(f"https://api.twitch.tv/helix/clips?game_id={g['id']}&first={nb_target}&started_at={date_limit}", headers=h).json().get('data', [])
                else:
                    streams = requests.get("https://api.twitch.tv/helix/streams?language=fr&first=40", headers=h).json().get('data', [])
                    for s in streams:
                        cls = requests.get(f"https://api.twitch.tv/helix/clips?broadcaster_id={s['user_id']}&first=3&started_at={date_limit}", headers=h).json().get('data', [])
                        found.extend(cls)
                    found = sorted(found, key=lambda x: x['view_count'], reverse=True)[:nb_target]
            
            st.session_state.clips = found
            st.success(f"{len(found)} CLIPS DETECTES")
        except Exception as e: st.error(f"ERREUR: {e}")

with tab_render:
    if st.session_state.clips:
        mode = st.radio("Style de Titrage", ["SERIEUX (Twitch)", "TROLL (Dictionnaire)"], horizontal=True)
        if st.button("LANCER LA MACHINE"):
            pb = st.progress(0)
            log = st.empty()
            for i, clip in enumerate(st.session_state.clips):
                if mode == "TROLL (Dictionnaire)":
                    f = random.choice(FEMMES_BASE)
                    a = random.choice(ATTR_BASE)
                    act = random.choice(ACTIONS_BASE)
                    l = random.choice(LIEUX_BASE)
                    # Modification ici : retrait de "DE" pour plus de fluidité
                    titre = f"{clip['broadcaster_name'].upper()} {act} {a} DE {f.upper()} {l}"
                else:
                    titre = f"{clip['broadcaster_name'].upper()} : {clip['title'].upper()}"
                
                log.info(f"RENDU: {titre}")
                loop.run_until_complete(process_video(clip, titre, i, log))
                pb.progress((i+1)/len(st.session_state.clips))
            st.success("PRODUCTION TERMINEE")
    else:
        st.info("SCANNEZ DES CLIPS POUR COMMENCER")
