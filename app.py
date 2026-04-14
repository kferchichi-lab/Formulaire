import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Suivi Arrêts TPR", page_icon="📝", layout="wide")

# --- STYLE CSS ---
st.markdown("""
    <style>
        .stMetric { background-color: #ffffff; padding: 10px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .temp-header { color: #0047AB; font-weight: bold; border-bottom: 2px solid #0047AB; margin-bottom: 10px; }
        .stButton > button {
            width: 100%; background: linear-gradient(135deg, #0047AB 0%, #00264d 100%);
            color: white !important; font-weight: bold; border-radius: 8px; height: 3em;
        }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION DES PRESSES ---
CONFIG_PRESSES = {
    "Presse 4": {"diametre": 228},
    "Presse 6": {"diametre": 178},
    "Presse 7": {"diametre": 178},
}

# --- SIDEBAR : CHOIX ET RAPPELS ---
with st.sidebar:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6q1BtDSDgVnJZFo0hOBfQJoDS6OYiub-qfQ&s", width=100)
    st.header("⚙️ Configuration")
    presse_choisie = st.selectbox("SÉLECTIONNER LA PRESSE :", options=list(CONFIG_PRESSES.keys()), index=None, placeholder="Choisir...")
    
    st.divider()
    
    st.markdown("<div class='temp-header'>🌡️ RAPPEL TEMPÉRATURES</div>", unsafe_allow_html=True)
    st.info("""
    - **Conteneur :** 400 - 430°C
    - **Filière :** 450°C
    - **Lopin (Plate) :** 440 - 470°C
    - **Lopin (Tubulaire) :** 470 - 510°C
    """)
    st.warning("⚠️ Tolérance : +/- 10°C")

# --- CONTENU PRINCIPAL ---
st.title("📝 Signalement Arrêt Production (Chapeau)")

if not presse_choisie:
    st.warning("👈 Veuillez sélectionner une presse dans le menu à gauche pour accéder au formulaire.")
    st.stop()

st.subheader(f"Saisie des données : {presse_choisie}")

# --- FORMULAIRE ---
with st.form("form_diagnostic", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        date_j = st.date_input("Date du jour", datetime.now())
        poste = st.radio("Poste de travail", ["A", "B", "C"], horizontal=True)
        ref_filiere = st.text_input("Référence Filière", placeholder="Ex: F105")
    
    with col
