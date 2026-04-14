import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Suivi Arrêts TPR", page_icon="📝", layout="wide")

# --- FICHIER DE BASE DE DONNÉES ---
DB_FILE = "base_donnees_chapeaux.csv"

# Fonction pour sauvegarder les données dans le fichier CSV
def sauvegarder_donnees(data):
    df = pd.DataFrame([data])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False, sep=";", encoding="utf-8-sig")
    else:
        df.to_csv(DB_FILE, mode='a', index=False, header=False, sep=";", encoding="utf-8-sig")

# --- STYLE CSS ---
st.markdown("""
    <style>
        header { visibility: visible !important; height: 60px !important; }
        .block-container { padding-top: 2rem !important; }
        .temp-header { color: #0047AB; font-weight: bold; margin-bottom: 5px; }
        
        /* Bouton Enregistrer Premium */
        div.stButton > button {
            width: 100%; height: 3.5em; border-radius: 12px; border: none;
            background: linear-gradient(135deg, #0047AB 0%, #00264d 100%);
            color: white !important; font-size: 16px !important; font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(0, 71, 171, 0.3);
            transition: all 0.3s;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 71, 171, 0.5) !important;
        }
    </style>
    """, unsafe_allow_html=True)

CONFIG_PRESSES = {
    "Presse 4": {"diametre": 228},
    "Presse 6": {"diametre": 178},
    "Presse 7": {"diametre": 178},
}

# --- SIDEBAR : CHOIX ET RAPPELS ---
with st.sidebar:
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


# --- LOGOS ET TITRE ---
col_logo, col_titre = st.columns([1, 4])
with col_logo:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6q1BtDSDgVnJZFo0hOBfQJoDS6OYiub-qfQ&s", width=120)
with col_titre:
    st.markdown("## Tunisie Profilés d'Aluminium")
    st.markdown("#### Direction Maintenance et Travaux Neufs")

st.divider()

# --- NAVIGATION PAR ONGLETS ---
tab_saisie, tab_base = st.tabs(["➕ Nouvelle Saisie", "📊 Consulter la Base de Données"])

# --- ONGLET 1 : FORMULAIRE DE SAISIE ---
with tab_saisie:
    if not presse_choisie:
        st.info("👈 Veuillez sélectionner une presse dans le menu à gauche pour accéder au formulaire.")
    else:
        st.subheader(f"📝 Saisie d'incident : {presse_choisie}")
        with st.form("form_diagnostic", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                date_j = st.date_input("Date de l'arrêt", datetime.now())
                poste = st.radio("Poste de travail", ["A", "B", "C"], horizontal=True)
                ref_filiere = st.text_input("Référence Filière", placeholder="Ex: 52000")
            
            with col2:
                num_lopin = st.text_input("Numéro du lopin", placeholder="Ex: 12")
                duree = st.number_input("Durée de l'arrêt (minutes)", min_value=0, step=1)
                cause = st.selectbox("Cause identifiée (Code)", [
                    "T - Problème de Température non homogène (Filière, conteneur, lopin)",
                    "H - Problème Hydraulique (Pression de bridage, de chape…)",
                    "O - Outillage : face de contact entre conteneur et filière (Usure, casse…)",
                    "R - Raclage du conteneur : Lopin déformé, 2 morceaux du lopin non alignés..",
                ])

            commentaire = st.text_area("Observations / Détails de l'incident")
            submitted = st.form_submit_button("ENREGISTRER L'INCIDENT")

            if submitted:
                if not ref_filiere or not num_lopin:
                    st.error("Veuillez remplir les champs obligatoires (Filière et Lopin).")
                else:
                    # Préparation de la ligne de données
                    nouvelle_entree = {
                        "Date": date_j.strftime("%d/%m/%Y"),
                        "Heure_Saisie": datetime.now().strftime("%H:%M:%S"),
                        "Presse": presse_choisie,
                        "Poste": poste,
                        "Filiere": ref_filiere,
                        "Lopin": num_lopin,
                        "Duree_Min": duree,
                        "Cause": cause,
                        "Observations": commentaire
                    }
                    sauvegarder_donnees(nouvelle_entree)
                    st.success(f"✅ Incident enregistré pour la {presse_choisie}")
                    st.snow()

# --- ONGLET 2 : CONSULTATION DE LA BASE ---
with tab_base:
    st.subheader("📊 Historique Global des Arrêts")
    if os.path.isfile(DB_FILE):
        df_affichage = pd.read_csv(DB_FILE, sep=";")
        
        # Filtres interactifs
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtre_presse = st.multiselect("Filtrer par Presse :", options=df_affichage["Presse"].unique())
        with col_f2:
            filtre_cause = st.multiselect("Filtrer par Cause :", options=df_affichage["Cause"].unique())
        
        if filtre_presse:
            df_affichage = df_affichage[df_affichage["Presse"].isin(filtre_presse)]
        if filtre_cause:
            df_affichage = df_affichage[df_affichage["Cause"].isin(filtre_cause)]
            
        # Affichage du tableau (Le Grand Tableau)
        st.dataframe(df_affichage, use_container_width=True)
        
        # Bouton d'export Excel
        csv = df_affichage.to_csv(index=False, sep=";").encode('utf-8-sig')
        st.download_button(
            label="📥 Télécharger la base complète pour Excel",
            data=csv,
            file_name=f"base_arrets_TPR_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime="text/csv",
        )
    else:
        st.info("Aucune donnée n'a encore été enregistrée.")

# --- FOOTER ---
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="text-align: center; color: gray; font-size: 0.8em; border-top: 1px solid #eee; padding-top: 10px;">
        © 2026 TPR - Système de Suivi Maintenance <br>
        Direction Maintenance et Travaux Neufs - DMTN 
    </div>
    """, 
    unsafe_allow_html=True
)
