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
st.title("📝 Suivi Arrêts Production : Problème Chapeaux")

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
    
    with col2:
        num_lopin = st.text_input("Numéro du lopin", placeholder="Ex: 12")
        duree = st.number_input("Durée de l'arrêt (minutes)", min_value=0, step=4)
        cause = st.selectbox("Cause identifiée (Code)", [
            "T - Problème de Température non homogène ( Filière, conteneur, lopin)",
            "H - Problème Hydraulique ( Pression de bridage, de chape…)",
            "O - Outillage : face de contact entre conteneur et filière ( Usure, casse…)",
            "R - Raclage du conteneur : Lopin déformé, 2 morceaux du lopin non alignés.. ",
            ])

    commentaire = st.text_area("Observations / Détails de l'incident")
    
    submitted = st.form_submit_button("ENREGISTRER L'INCIDENT")

# --- VALIDATION ---
if submitted:
    if not ref_filiere or not num_lopin:
        st.error("Veuillez remplir les champs obligatoires (Filière et Lopin).")
    else:
        st.success(f"Données enregistrées pour la {presse_choisie} - Code {cause[0]}")
        # Note : Ici vous pouvez connecter une base de données ou un fichier CSV
        st.snow()

# --- PIED DE PAGE ---
st.divider()
st.caption("Direction Maintenance et Travaux Neufs - TPR 2026")
