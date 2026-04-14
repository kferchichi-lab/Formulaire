import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Saisie Arrêt TPR", page_icon="📝", layout="centered")

DB_FILE = "base_donnees_chapeaux.csv"

def sauvegarder_donnees(data):
    df = pd.DataFrame([data])
    if not os.path.isfile(DB_FILE):
        df.to_csv(DB_FILE, index=False, sep=";", encoding="utf-8-sig")
    else:
        df.to_csv(DB_FILE, mode='a', index=False, header=False, sep=";", encoding="utf-8-sig")

# --- STYLE ---
st.markdown("""
    <style>
        .block-container { padding-top: 2rem; }
        div.stButton > button {
            width: 100%; height: 4em; border-radius: 12px;
            background: linear-gradient(135deg, #0047AB 0%, #00264d 100%);
            color: white !important; font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6q1BtDSDgVnJZFo0hOBfQJoDS6OYiub-qfQ&s", width=100)
    presse_choisie = st.selectbox("SÉLECTIONNER LA PRESSE :", ["Presse 4", "Presse 6", "Presse 7"], index=None)
    st.divider()
    st.info("**🌡️ RAPPELS :**\n\nConteneur: 400-430°C\n\nFilière: 450°C\n\nLopin Plate: 440-470°C\n\nLopin Tub: 470-510°C")

# --- FORMULAIRE ---
st.title("📝 Signalement Incident")

if not presse_choisie:
    st.warning("👈 Sélectionnez votre presse à gauche.")
    st.stop()

with st.form("form_op", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        date_j = st.date_input("Date", datetime.now())
        poste = st.radio("Poste", ["A", "B", "C"], horizontal=True)
        ref_f = st.text_input("Référence Filière")
    with col2:
        num_l = st.text_input("N° Lopin")
        duree = st.number_input("Durée (min)", min_value=0, step=1)
        cause = st.selectbox("Cause", [
            "T - Température non homogène",
            "H - Problème Hydraulique",
            "O - Outillage (Face de contact)",
            "R - Raclage du conteneur"
        ])
    obs = st.text_area("Observations")
    if st.form_submit_button("ENREGISTRER L'INCIDENT"):
        if ref_f and num_l:
            sauvegarder_donnees({
                "Date": date_j.strftime("%d/%m/%Y"), "Heure": datetime.now().strftime("%H:%M"),
                "Presse": presse_choisie, "Poste": poste, "Filiere": ref_f,
                "Lopin": num_l, "Duree_Min": duree, "Cause": cause, "Observations": obs
            })
            st.success("✅ Enregistré !")
            st.balloons()
        else:
            st.error("Champs manquants !")
