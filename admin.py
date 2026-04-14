import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="ADMIN - Dashboard TPR", page_icon="📊", layout="wide")

DB_FILE = "base_donnees_chapeaux.csv"

st.title("📊 Administration & Analyse des Arrêts")

if os.path.isfile(DB_FILE):
    df = pd.read_csv(DB_FILE, sep=";")
    
    # --- STATS RAPIDES ---
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Incidents", len(df))
    col_b.metric("Temps d'arrêt total (min)", df["Duree_Min"].sum())
    col_c.metric("Presse la plus touchée", df["Presse"].mode()[0])

    st.divider()

    # --- LE GRAND TABLEAU ---
    st.subheader("🔍 Base de données complète")
    f_presse = st.multiselect("Filtrer par Presse", df["Presse"].unique())
    if f_presse:
        df = df[df["Presse"].isin(f_presse)]
    
    st.dataframe(df, use_container_width=True)

    # --- BOUTON EXCEL ---
    csv = df.to_csv(index=False, sep=";").encode('utf-8-sig')
    st.download_button("📥 Télécharger pour Excel", data=csv, file_name="export_tpr.csv")

else:
    st.warning("Aucune donnée enregistrée pour le moment.")
