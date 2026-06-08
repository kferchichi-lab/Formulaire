import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px  # Pour les graphiques
import plotly.graph_objects as go # Pour le graphique combiné double axe
import io
import matplotlib.pyplot as plt
# Assurez-vous d'avoir fpdf2 installé (ajoutez-le à votre fichier requirements.txt : fpdf2)
from fpdf import FPDF

heure_locale = datetime.now() + timedelta(hours=1)

DB_FILE = "base_donnees_chapeaux.csv"

DICTIONNAIRE_CODES = {
    "R": ["Lopin déformé", "2 morceaux du lopin non alignés", "Conteneur encrassé", "Autre problème de raclage"],
    "O": ["Face de contact entre conteneur et filière", "Usure prématurée du grain", "Casse outillage", "Mauvais centrage"],
    "H": ["Pression de bridage insuffisante", "Pression de chape instable", "Fuite d'huile vérin", "Problème de pompe", "Pression d'extrusion instable"],
    "T": ["Température non homogène du conteneur", "Température de filière inadéquate", "Refroidissement du lopin"],
    "A": ["Attente matière", "Pause opérateur", "Panne électrique générale"]
}

st.set_page_config(page_title="Suivi Arrêts TPR", page_icon="📝", layout="wide")

def sauvegarder_donnees(data):
    df = pd.DataFrame([data])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False, sep=";", encoding="utf-8-sig")
    else:
        df.to_csv(DB_FILE, mode='a', index=False, header=False, sep=";", encoding="utf-8-sig")

st.markdown("""
    <style>
        header { visibility: visible !important; height: 60px !important; }
        .block-container { padding-top: 2rem !important; }
        .temp-header { color: #0047AB; font-weight: bold; margin-bottom: 5px; }

        header {
            visibility: visible !important;
            height: 60px !important;
        }
        
        .block-container {
            padding-top: 5rem !important; 
            padding-bottom: 2rem !important;
            padding-left: 5rem !important;
            padding-right: 5rem !important;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 3.5rem !important; 
                padding-left: 1.5rem !important;
                padding-right: 1.5rem !important;
            }
            
            [data-testid="stImage"] {
                margin-top: 10px !important;
            }
        }

        [data-testid="stImage"] img {
            max-width: 100%;
            height: auto;
            object-fit: contain !important;
        }
        
        div.stButton > button, 
        div.stDownloadButton > button, 
        div.stFormSubmitButton > button {
            width: 100% !important; 
            height: 3.5em !important; 
            border-radius: 12px !important; 
            border: none !important;
            background: linear-gradient(135deg, #0047AB 0%, #00264d 100%) !important;
            color: white !important; 
            font-size: 16px !important; 
            font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(0, 71, 171, 0.3) !important;
            transition: all 0.3s ease !important;
        }

        div.stButton > button:hover, 
        div.stDownloadButton > button:hover, 
        div.stFormSubmitButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 71, 171, 0.5) !important;
            background: linear-gradient(135deg, #0056cc 0%, #003366 100%) !important;
        }

        div.stButton > button p, 
        div.stDownloadButton > button p, 
        div.stFormSubmitButton > button p {
            color: white !important;
        }
        
        [data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }
        
        [data-testid="stForm"] > div:last-child {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            margin-top: 20px;
        }

        div.stDownloadButton {
            display: flex;
            justify-content: center;
            width: 100%;
            margin-top: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

CONFIG_PRESSES = {
    "Presse 4": {"diametre": 228},
    "Presse 6": {"diametre": 178},
    "Presse 7": {"diametre": 178},
}

with st.sidebar:
    st.header("⚙️ Configuration machine")
    presse_choisie = st.selectbox("Sélectionner une presse :", options=list(CONFIG_PRESSES.keys()), index=None, placeholder="Choisir...")
  
    st.divider()
    st.markdown("<div class='temp-header'>🌡️ RAPPEL TEMPÉRATURES</div>", unsafe_allow_html=True)
    st.info("""
    - **Conteneur :** 400 - 430°C
    - **Filière :** 450°C
    - **Lopin (Plate) :** 440 - 470°C
    - **Lopin (Tubulaire) :** 470 - 510°C
    """)
    st.warning("⚠️ Tolérance : +/- 10°C")

col_logo, col_titre = st.columns([1, 5])
with col_logo:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6q1BtDSDgVnJZFo0hOBfQJoDS6OYiub-qfQ&s", width=150)
with col_titre:
    st.markdown("## Tunisie Profilés d'Aluminium")
    st.markdown("#### Direction Maintenance et Travaux Neufs")
st.divider()

def generer_filtre_temporel(cle_unique):
    st.write("### 📅 Sélection de la Période d'Analyse")
    col_p1, col_p2 = st.columns([1, 2])
    with col_p1:
        choix_periode = st.selectbox(
            "Période de filtrage :",
            options=["Les dernières 24 heures", "Jour précédent", "Cette semaine", "Ce mois", "Cette année", "Personnalisée"],
            index=3, 
            key=f"choix_per_{cle_unique}"
        )
    aujourdhui = datetime.now().date()
    date_debut = aujourdhui
    date_fin = aujourdhui

    if choix_periode == "Les dernières 24 heures":
        date_debut = aujourdhui - timedelta(days=1)
        date_fin = aujourdhui
    elif choix_periode == "Jour précédent":
        date_debut = aujourdhui - timedelta(days=1)
        date_fin = aujourdhui - timedelta(days=1)
    elif choix_periode == "Cette semaine":
        date_debut = aujourdhui - timedelta(days=aujourdhui.weekday())
        date_fin = aujourdhui
    elif choix_periode == "Ce mois":
        date_debut = aujourdhui.replace(day=1)
        date_fin = aujourdhui
    elif choix_periode == "Cette année":
        date_debut = aujourdhui.replace(month=1, day=1)
        date_fin = aujourdhui
    elif choix_periode == "Personnalisée":
        with col_p2:
            mode_perso = st.radio("Sélectionner la méthode :", ["Un jour", "Plusieurs jours"], horizontal=True, key=f"mode_p_{cle_unique}")
            if mode_perso == "Un jour":
                date_choisie = st.date_input("Sélectionner le jour exact", aujourdhui, key=f"date_un_{cle_unique}")
                date_debut = date_choisie
                date_fin = date_choisie
            else:
                dates_choisies = st.date_input("Sélectionner la plage de dates", [aujourdhui - timedelta(days=7), aujourdhui], key=f"date_mult_{cle_unique}")
                if isinstance(dates_choisies, (list, tuple)):
                    if len(dates_choisies) == 2:
                        date_debut = dates_choisies[0]
                        date_fin = dates_choisies[1]
                    elif len(dates_choisies) == 1:
                        date_debut = dates_choisies[0]
                        date_fin = dates_choisies[0]
    return date_debut, date_fin, choix_periode


tab_saisie, tab_base, tab_stats = st.tabs(["➕ Nouvelle saisie", "📊 Consulter la base de données", "📈 Analyse graphique"])

# =========================================================================
# ➕ ONGLET 1 : SAISIE
# =========================================================================
with tab_saisie:
    if not presse_choisie:
        st.info("👈 Veuillez sélectionner une presse dans le menu à gauche pour accéder au formulaire.")
    else:
        st.subheader(f"📝 Saisie d'incident : {presse_choisie}")
        col1, col2 = st.columns(2)
        with col1:
            date_j = st.date_input("Date de l'arrêt", datetime.now())
            poste = st.radio("Poste de travail", ["A", "B", "C"], horizontal=True)
            ref_filiere = st.text_input("Référence de la filière", placeholder="Ex: 52000")
       
        with col2:
            num_lopin = st.text_input("Numéro du lopin", placeholder="Ex: 12")
            duree = st.number_input("Durée de l'arrêt (minutes)", min_value=0, step=1)
            
            cause_principale = st.selectbox(
                "Nature de la cause (Générale) :",
                options=[
                    "R - Raclage du conteneur",
                    "O - Outillage",
                    "H - Problème hydraulique",
                    "T - Problème de température",
                    "A - Autres"
                ],
                index=None,  
                placeholder="--- Choisir une cause générale ---", 
                key="cause_gnerale_select"
            )
            raisons_finales_texte = "Non spécifié"
            if cause_principale is not None:
                code_lettre = cause_principale[0]
                raisons_disponibles = DICTIONNAIRE_CODES.get(code_lettre, DICTIONNAIRE_CODES["A"])

                st.write("**Sélectionnez la ou les raisons détaillées :**")
                raisons_choisies = []

                for raison in raisons_disponibles:
                    if st.checkbox(raison, key=f"cb_{code_lettre}_{raison}"):
                        raisons_choisies.append(raison)

                raisons_finales_texte = ", ".join(raisons_choisies) if raisons_choisies else "Non spécifié"
                cause_finale = f"{cause_principale} : {raisons_finales_texte}"
            else:
                st.info("💡 Veuillez sélectionner une nature de cause pour voir les raisons détaillées.")

        commentaire = st.text_area("Observations / Détails de l'incident")
        
        with st.form("form_validation", clear_on_submit=True):
            submitted = st.form_submit_button("ENREGISTRER L'INCIDENT")
        if submitted:
            if not ref_filiere or not num_lopin:
                st.error("Veuillez remplir les champs obligatoires (Filière et Lopin).")
            elif raisons_finales_texte == "Non spécifié":
                st.warning("⚠️ Veuillez cocher au moins une raison détaillée avant d'enregistrer.")
            else:
                nouvelle_entree = {
                    "Date": date_j.strftime("%d/%m/%Y"),
                    "Heure_Saisie": datetime.now().strftime("%H:%M:%S"),
                    "Presse": presse_choisie,
                    "Poste": poste,
                    "Filiere": ref_filiere,
                    "Lopin": num_lopin,
                    "Duree_Min": duree,
                    "Cause": cause_finale, 
                    "Observations": commentaire
                }
                sauvegarder_donnees(nouvelle_entree)
                st.success(f"✅ Incident enregistré pour la {presse_choisie}")

# =========================================================================
# 📊 ONGLET 2 : CONSULTATION BASE DE DONNÉES
# =========================================================================
with tab_base:
    date_debut_filtre, date_fin_filtre, choix_periode = generer_filtre_temporel("base")
    st.divider()

    st.subheader("📊 Historique Global des Arrêts")
    if os.path.isfile(DB_FILE):
        df_affichage = pd.read_csv(DB_FILE, sep=";")
        
        if "Cause" in df_affichage.columns:
            df_affichage['Cause'] = df_affichage['Cause'].fillna("A - Autres")
            mapping_filtres = {
                "R": "R - Raclage du conteneur",
                "O": "O - Outillage",
                "H": "H - Problème Hydraulique",
                "T": "T - Problème de Température",
                "A": "A - Autres"
            }
            df_affichage['Cause_Filtre_Standard'] = df_affichage['Cause'].str[0].str.upper().map(mapping_filtres).fillna("A - Autres")
        else:
            df_affichage['Cause'] = "A - Autres"
            df_affichage['Cause_Filtre_Standard'] = "A - Autres"

        if 'Date' in df_affichage.columns:
            df_affichage['Date_Parsed'] = pd.to_datetime(df_affichage['Date'], format='%d/%m/%Y', errors='coerce').dt.date
            df_affichage['Date'] = df_affichage['Date'].astype(str).str[:10]
        if 'Duree_Min' in df_affichage.columns:
            df_affichage['Duree_Min'] = pd.to_numeric(df_affichage['Duree_Min'], errors='coerce').fillna(0).astype(int)

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            options_presse = df_affichage["Presse"].unique() if "Presse" in df_affichage.columns else []
            filtre_presse = st.multiselect("Filtrer par Presse :", options=options_presse)
        with col_f2:
            options_cause = sorted(df_affichage["Cause_Filtre_Standard"].unique())
            filtre_cause = st.multiselect("Filtrer par Cause :", options=options_cause)
       
        df_filtre = df_affichage.copy()
        if date_debut_filtre is not None and date_fin_filtre is not None:
            df_filtre = df_filtre[(df_filtre['Date_Parsed'] >= date_debut_filtre) & (df_filtre['Date_Parsed'] <= date_fin_filtre)]
            
        if filtre_presse:
            df_filtre = df_filtre[df_filtre["Presse"].
