import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Suivi Arrêts TPR", page_icon="📝", layout="wide")

# --- STYLE CSS ---
st.markdown("""
    <style>
        /* On rend le header système visible pour la flèche mobile */
        header {
            visibility: visible !important;
            height: 60px !important;
        }
        
        /* --- CONFIGURATION PC (Par défaut) --- */
        .block-container {
            padding-top: 5rem !important; /* On augmente ici pour éviter le crop PC */
            padding-bottom: 2rem !important;
            padding-left: 5rem !important;
            padding-right: 5rem !important;
        }

        /* --- CONFIGURATION SMARTPHONE --- */
        @media (max-width: 768px) {
            .block-container {
                padding-top: 3.5rem !important; /* Un peu moins pour mobile pour garder votre 'très bon' rendu */
                padding-left: 1.5rem !important;
                padding-right: 1.5rem !important;
            }
            
            [data-testid="stImage"] {
                margin-top: 10px !important;
            }
        }

        /* Sécurité pour l'image (Logo) */
        [data-testid="stImage"] img {
            max-width: 100%;
            height: auto;
            object-fit: contain !important;
        }
       /* Style des barres de visualisation */
        .container-barre { width: 100%; background-color: #e0e0e0; border-radius: 5px; height: 20px; position: relative;}
        .barre-lopin { background-color: #808080; height: 100%; border-radius: 5px; transition: width 0.5s;}
        .barre-limite { background-color: #1a4332; height: 8px; border-radius: 5px; margin-top: 4px;}
        
       /* --- BOUTON CALCULER PREMIUM --- */
        div.stButton > button {
            width: 100%; 
            height: 3.8em;
            border-radius: 12px;
            border: none;
            
            /* Dégradé de bleu professionnel */
            background: linear-gradient(135deg, #0047AB 0%, #00264d 100%);
            color: white !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px;
            
            /* Ombre portée pour le relief */
            box-shadow: 0 4px 15px rgba(0, 71, 171, 0.3);
            transition: all 0.3s ease-in-out;
            cursor: pointer;
        }

        /* --- EFFET AU SURVOL (HOVER) --- */
        div.stButton > button:hover {
            background: linear-gradient(135deg, #0056d6 0%, #0047AB 100%) !important;
            color: white !important;
            box-shadow: 0 6px 20px rgba(0, 71, 171, 0.5) !important;
            transform: translateY(-2px); /* Le bouton remonte légèrement */
            border: none !important;
        }

        /* --- EFFET AU CLIC (ACTIVE) --- */
        div.stButton > button:active {
            transform: translateY(1px) scale(0.98);
            box-shadow: 0 2px 10px rgba(0, 71, 171, 0.2) !important;
        }
    </style>
    """, unsafe_allow_html=True)
CONFIG_PRESSES = {
    "Presse 4": {"diametre": 228, "limite_longueur": 1150},
    "Presse 6": {"diametre": 178, "limite_longueur": 890},
    "Presse 7": {"diametre": 178, "limite_longueur": 1000},
}

# --- SIDEBAR : CHOIX ET RAPPELS ---
with st.sidebar:
    st.header("⚙️ Configuration Machine")
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
