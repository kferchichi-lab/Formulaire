import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px  # Pour les graphiques
from io import BytesIO      # Pour l'export Excel

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Suivi Arrêts TPR", page_icon="📝", layout="wide")

# --- FICHIER DE BASE DE DONNÉES ---
DB_FILE = "base_donnees_chapeaux.csv"

# Fonction pour sauvegarder les données
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
        div.stButton > button {
            width: 100%; height: 3.5em; border-radius: 12px; border: none;
            background: linear-gradient(135deg, #0047AB 0%, #00264d 100%);
            color: white !important; font-size: 16px !important; font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(0, 71, 171, 0.3);
            transition: all 0.3s;
        }
    </style>
    """, unsafe_allow_html=True)

CONFIG_PRESSES = {
    "Presse 4": {"diametre": 228},
    "Presse 6": {"diametre": 178},
    "Presse 7": {"diametre": 178},
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration Machine")
    presse_choisie = st.selectbox("SÉLECTIONNER LA PRESSE :", options=list(CONFIG_PRESSES.keys()), index=None, placeholder="Choisir...")
    st.divider()
    st.markdown("<div class='temp-header'>🌡️ RAPPEL TEMPÉRATURES</div>", unsafe_allow_html=True)
    st.info("- **Conteneur :** 400 - 430°C\n- **Filière :** 450°C\n- **Lopin (Plate) :** 440 - 470°C\n- **Lopin (Tubulaire) :** 470 - 510°C")

# --- LOGOS ET TITRE ---
col_logo, col_titre = st.columns([1, 5])
with col_logo:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6q1BtDSDgVnJZFo0hOBfQJoDS6OYiub-qfQ&s", width=150)
with col_titre:
    st.markdown("## Tunisie Profilés d'Aluminium")
    st.markdown("#### Direction Maintenance et Travaux Neufs")

st.divider()

tab_saisie, tab_base, tab_stats = st.tabs(["➕ Nouvelle Saisie", "📊 Base de Données", "📈 Analyse Graphique"])

# --- ONGLET 1 : SAISIE ---
with tab_saisie:
    if not presse_choisie:
        st.info("👈 Veuillez sélectionner une presse à gauche.")
    else:
        with st.form("form_diagnostic", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                date_j = st.date_input("Date de l'arrêt", datetime.now())
                poste = st.radio("Poste", ["A", "B", "C"], horizontal=True)
                ref_filiere = st.text_input("Référence Filière")
            with col2:
                num_lopin = st.text_input("Numéro du lopin")
                duree = st.number_input("Durée (min)", min_value=0)
                cause = st.selectbox("Cause", ["T - Température", "H - Hydraulique", "O - Outillage", "R - Raclage", "Autres.."])
            
            commentaire = st.text_area("Observations")
            if st.form_submit_button("ENREGISTRER"):
                if ref_filiere and num_lopin:
                    sauvegarder_donnees({"Date": date_j.strftime("%d/%m/%Y"), "Presse": presse_choisie, "Poste": poste, "Filiere": ref_filiere, "Lopin": num_lopin, "Duree_Min": duree, "Cause": cause, "Observations": commentaire})
                    st.success("Enregistré !")
                    st.snow()

# --- ONGLET 2 : CONSULTATION & EXCEL ---
with tab_base:
    if os.path.isfile(DB_FILE):
        df = pd.read_csv(DB_FILE, sep=";")
        st.dataframe(df, use_container_width=True)
        
        # --- FONCTION EXPORT EXCEL ---
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Arrêts')
            return output.getvalue()

        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            st.download_button(label="📥 Télécharger EXCEL (.xlsx)", data=to_excel(df), file_name=f"arrets_TPR_{datetime.now().strftime('%d_%m_%Y')}.xlsx")
    else:
        st.info("Aucune donnée.")

# --- ONGLET 3 : ANALYSE GRAPHIQUE ---
with tab_stats:
    if os.path.isfile(DB_FILE):
        df_stats = pd.read_csv(DB_FILE, sep=";")
        st.subheader("Analyse des causes par Presse")
        
        # Sélecteur pour le graphique
        presse_filtre = st.multiselect("Sélectionner les presses à analyser :", options=df_stats["Presse"].unique(), default=df_stats["Presse"].unique())
        
        if presse_filtre:
            df_filtered = df_stats[df_stats["Presse"].isin(presse_filtre)]
            
            # Création du graphique en cercle (Pie Chart)
            # On groupe par 'Cause' et on compte les occurrences
            fig = px.pie(df_filtered, names='Cause', title=f"Répartition des causes - {', '.join(presse_filtre)}",
                         hole=0.4, # Pour en faire un Donut chart (plus moderne)
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
            
            # Optionnel : Répartition du temps d'arrêt
            st.divider()
            st.subheader("Total des minutes d'arrêt par cause")
            fig2 = px.bar(df_filtered, x='Cause', y='Duree_Min', color='Presse', barmode='group', title="Durée totale des arrêts par cause (min)")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Enregistrez des données pour voir les graphiques.")

# --- FOOTER ---
st.markdown("<div style='text-align: center; color: gray; font-size: 0.8em; border-top: 1px solid #eee; padding-top: 10px;'>© 2026 TPR - DMTN</div>", unsafe_allow_html=True)
