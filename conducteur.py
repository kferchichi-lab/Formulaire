import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import plotly.express as px  # Pour les graphiques
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

# =========================================================================
# 📅 BLOCK DE DÉFINITION DE LA PÉRIODE (Placé en haut pour portée globale)
# =========================================================================
st.write("### 📅 Sélection de la Période d'Analyse")
col_p1, col_p2 = st.columns([1, 2])

with col_p1:
    choix_periode = st.selectbox(
        "Période de filtrage :",
        options=["Les dernières 24 heures", "Jour précédent", "Cette semaine", "Ce mois", "Cette année", "Personnalisée"],
        index=0
    )

aujourdhui = datetime.now().date()
date_debut_filtre = aujourdhui
date_fin_filtre = aujourdhui

if choix_periode == "Les dernières 24 heures":
    date_debut_filtre = aujourdhui - timedelta(days=1)
    date_fin_filtre = aujourdhui
elif choix_periode == "Jour précédent":
    date_debut_filtre = aujourdhui - timedelta(days=1)
    date_fin_filtre = aujourdhui - timedelta(days=1)
elif choix_periode == "Cette semaine":
    date_debut_filtre = aujourdhui - timedelta(days=aujourdhui.weekday())
    date_fin_filtre = aujourdhui
elif choix_periode == "Ce mois":
    date_debut_filtre = aujourdhui.replace(day=1)
    date_fin_filtre = aujourdhui
elif choix_periode == "Cette année":
    date_debut_filtre = aujourdhui.replace(month=1, day=1)
    date_fin_filtre = aujourdhui
elif choix_periode == "Personnalisée":
    with col_p2:
        mode_perso = st.radio("Sélectionner la méthode :", ["Un jour", "Plusieurs jours"], horizontal=True)
        if mode_perso == "Un jour":
            date_choisie = st.date_input("Sélectionner le jour exact", aujourdhui)
            date_debut_filtre = date_choisie
            date_fin_filtre = date_choisie
        else:
            dates_choisies = st.date_input("Sélectionner la plage de dates", [aujourdhui - timedelta(days=7), aujourdhui])
            if isinstance(dates_choisies, (list, tuple)):
                if len(dates_choisies) == 2:
                    date_debut_filtre = dates_choisies[0]
                    date_fin_filtre = dates_choisies[1]
                elif len(dates_choisies) == 1:
                    date_debut_filtre = dates_choisies[0]
                    date_fin_filtre = dates_choisies[0]

st.divider()

# Initialisation des onglets après la sélection temporelle globale
tab_saisie, tab_base, tab_stats = st.tabs(["➕ Nouvelle saisie", "📊 Consulter la base de données", "📈 Analyse graphique"])

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

with tab_base:
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

        # Filtres interactifs complémentaires (Presse / Cause)
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            options_presse = df_affichage["Presse"].unique() if "Presse" in df_affichage.columns else []
            filtre_presse = st.multiselect("Filtrer par Presse :", options=options_presse)
        with col_f2:
            options_cause = sorted(df_affichage["Cause_Filtre_Standard"].unique())
            filtre_cause = st.multiselect("Filtrer par Cause :", options=options_cause)
       
        # APPLICATION STRICTE ET SÉCURISÉE DU FILTRE DE DATE GLOBAL
        df_filtre = df_affichage.copy()
        if date_debut_filtre is not None and date_fin_filtre is not None:
            df_filtre = df_filtre[(df_filtre['Date_Parsed'] >= date_debut_filtre) & (df_filtre['Date_Parsed'] <= date_fin_filtre)]
            
        if filtre_presse:
            df_filtre = df_filtre[df_filtre["Presse"].isin(filtre_presse)]
        if filtre_cause:
            df_filtre = df_filtre[df_filtre["Cause_Filtre_Standard"].isin(filtre_cause)]
           
        colonnes_visibles = ['Date', 'Presse', 'Poste', 'Filiere', 'Lopin', 'Duree_Min', 'Cause']
        colonnes_existantes = [c for c in colonnes_visibles if c in df_filtre.columns]
        
        df_pour_affichage = df_filtre[colonnes_existantes].copy()
        
        traductions = {
            'Date': 'Date', 'Presse': 'Presse', 'Poste': 'Poste', 
            'Filiere': 'Filière', 'Lopin': 'Lopin', 
            'Duree_Min': 'Durée (Min)', 'Cause': "Cause de l'arrêt"
        }
        df_pour_affichage.rename(columns=traductions, inplace=True)
            
        st.dataframe(df_pour_affichage, use_container_width=True, hide_index=True)

        csv = df_pour_affichage.to_csv(index=False, sep=";").encode('utf-8-sig')
        st.download_button(
            label="📥 Télécharger la base filtrée pour Excel",
            data=csv,
            file_name=f"base_arrets_TPR_{datetime.now().strftime('%d_%m_%Y')}.csv",
            mime="text/csv",
        )
    else:
        st.info("Aucune donnée n'a encore été enregistrée.")

with tab_stats:
    if os.path.isfile(DB_FILE):
        df_stats = pd.read_csv(DB_FILE, sep=";")
        
        if 'Date' in df_stats.columns:
            df_stats['Date_Parsed'] = pd.to_datetime(df_stats['Date'], format='%d/%m/%Y', errors='coerce').dt.date
        
        # APPLICATION DU MÊME FILTRE DE DATE ICI AUSSI
        if date_debut_filtre is not None and date_fin_filtre is not None:
            df_stats = df_stats[(df_stats['Date_Parsed'] >= date_debut_filtre) & (df_stats['Date_Parsed'] <= date_fin_filtre)]

        st.subheader("Analyse des causes par Presse")
        presse_filtre = st.multiselect("Sélectionner les presses à analyser :", options=df_stats["Presse"].unique() if not df_stats.empty else [], default=df_stats["Presse"].unique() if not df_stats.empty else [])
        
        if not df_stats.empty and presse_filtre:
            df_filtered = df_stats[df_stats["Presse"].isin(presse_filtre)].copy()
            df_filtered['Cause'] = df_filtered['Cause'].fillna("A")
            df_filtered['Code_Lettre'] = df_filtered['Cause'].str[0].str.upper()
            
            mapping_noms = {
                "R": "R - Raclage du conteneur",
                "O": "O - Outillage",
                "H": "H - Problème Hydraulique",
                "T": "T - Problème de Température",
                "A": "A - Autres"
            }
            df_filtered['Cause_Standard'] = df_filtered['Code_Lettre'].map(mapping_noms).fillna("A - Autres")
            
            if df_filtered.empty:
                st.warning("⚠️ Aucune donnée valide trouvée pour la période sélectionnée.")
            else:
                fig = px.pie(
                    df_filtered, 
                    names='Cause_Standard',
                    title=f"Répartition des causes - {', '.join(presse_filtre)}",
                    hole=0.4, 
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig.update_traces(textposition='inside', textinfo='percent')
                fig.update_layout(legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05))
                st.plotly_chart(fig, use_container_width=True)

            st.divider()
            
            if not df_filtered.empty:
                df_temp = df_filtered.copy()
                df_temp['Code_Cause'] = df_temp['Code_Lettre']

                st.subheader("Total des minutes d'arrêt par cause")
                fig2 = px.bar(
                    df_temp, 
                    x='Code_Cause', 
                    y='Duree_Min', 
                    color='Presse', 
                    barmode='group',
                    title="Durée totale des arrêts par code de cause (min)",
                    labels={'Code_Cause': 'Cause (Code)', 'Duree_Min': 'Minutes'},
                    color_discrete_map={"Presse 4": "#E63946", "Presse 6": "#457B9D", "Presse 7": "#2A9D8F"}
                )
                fig2.update_traces(marker_line_color='white', marker_line_width=1, opacity=0.9)
                fig2.update_layout(xaxis_tickangle=0)    
                st.plotly_chart(fig2, use_container_width=True)
        
                df_filtered['Code'] = df_filtered['Cause'].str[0]
                tableau_somme = df_filtered.groupby('Code')['Duree_Min'].sum().reset_index()
                tableau_somme = tableau_somme.sort_values(by='Duree_Min', ascending=False)          
                tableau_somme.columns = ['Code Cause', 'Temps Total (Minutes)']
                col_vide, col_tab, col_espace, col_metrique = st.columns([1, 2, 0.5, 2])

                with col_tab:
                    st.dataframe(tableau_somme, use_container_width=False, hide_index=True, width=400)

                with col_metrique:
                    st.markdown("<br><br>", unsafe_allow_html=True)
                    total_general = tableau_somme['Temps Total (Minutes)'].sum()
                    st.metric("TOTAL GÉNÉRAL", f"{total_general} min")
        
                st.info("**Rappel des codes :** **T** : Problème de Température | **H** : Problème Hydraulique | **O** : Outillage | **R** : Raclage | **A** : Autres..")
                st.write("### 📄 Rapport d'Activité PDF")
                
                if st.button("📊 Générer le Rapport PDF Analytique", key="btn_pdf"):
                    with st.spinner("Création du rapport PDF en cours..."):
                        df_pie = df_filtered.groupby('Cause_Standard').size().reset_index(name='Nombre')
                        
                        fig_pdf1, ax_pdf1 = plt.subplots(figsize=(6, 4))
                        ax_pdf1.pie(df_pie['Nombre'], labels=df_pie['Cause_Standard'], autopct='%1.1f%%', startangle=90,
                                    colors=['#4ed0db', '#fcd170', '#ff9f73', '#d0a2f7', '#70a1ff'])
                        ax_pdf1.axis('equal')
                        plt.title("Répartition des Causes d'Arrêt", fontsize=12, fontweight='bold', pad=10)
                        
                        img_buf1 = io.BytesIO()
                        plt.savefig(img_buf1, format='png', bbox_inches='tight', dpi=150)
                        img_buf1.seek(0)
                        plt.close()

                        df_bar_pdf = df_filtered.groupby(['Code_Lettre', 'Presse'])['Duree_Min'].sum().unstack().fillna(0)
                        fig_pdf2, ax_pdf2 = plt.subplots(figsize=(7, 3.5))
                        df_bar_pdf.plot(kind='bar', ax=ax_pdf2, width=0.6, edgecolor='black', alpha=0.9)
                        ax_pdf2.set_ylabel("Minutes", fontsize=10)
                        ax_pdf2.set_xlabel("Cause (Code)", fontsize=10)
                        ax_pdf2.set_title("Durée Totale des Arrêts par Code de Cause (min)", fontsize=12, fontweight='bold', pad=10)
                        plt.xticks(rotation=0)
                        plt.grid(axis='y', linestyle='--', alpha=0.5)
                        
                        img_buf2 = io.BytesIO()
                        plt.savefig(img_buf2, format='png', bbox_inches='tight', dpi=150)
                        img_buf2.seek(0)
                        plt.close()

                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_fill_color(30, 39, 44) 
                        pdf.rect(0, 0, 210, 35, 'F')
                        
                        pdf.set_text_color(255, 255, 255)
                        pdf.set_font("Arial", 'B', 16)
                        pdf.cell(0, 12, "RAPPORT ANALYTIQUE DES INCIDENTS - CHAPEAUX", ln=True, align='C')
                        pdf.set_font("Arial", 'I', 10)
                        pdf.cell(0, 5, "Suivi de la Performance de Production & Maintenance - TPR", ln=True, align='C')
                        
                        pdf.ln(15)
                        pdf.set_text_color(0, 0, 0)
                        
                        pdf.set_font("Arial", 'B', 11)
                        pdf.cell(40, 7, "Date de génération :", 0)
                        pdf.set_font("Arial", '', 11)
                        pdf.cell(60, 7, heure_locale.strftime('%d/%m/%Y à %H:%M'), 0, True)
                        
                        pdf.set_font("Arial", 'B', 11)
                        pdf.cell(40, 7, "Filtre Presse(s) :", 0)
                        pdf.set_font("Arial", '', 11)
                        pdf.cell(60, 7, ", ".join(presse_filtre), 0, True)
                        
                        pdf.set_font("Arial", 'B', 11)
                        pdf.cell(40, 7, "Période analysée :", 0)
                        pdf.set_font("Arial", '', 11)
                        pdf.cell(60, 7, choix_periode, 0, True)
                        
                        pdf.line(10, 60, 200, 60)
                        pdf.ln(8)
                        
                        pdf.set_font("Arial", 'B', 13)
                        pdf.cell(0, 8, "1. Répartition Proportionnelle des Défaillances", ln=True)
                        pdf.ln(2)
                        pdf.image(img_buf1, x=35, w=140)
                        pdf.ln(10)
                        
                        pdf.set_font("Arial", 'B', 13)
                        pdf.cell(0, 8, "2. Analyse Quantifiée des Temps d'Arrêt", ln=True)
                        pdf.ln(2)
                        pdf.image(img_buf2, x=20, w=170)
                        
                        pdf.set_y(-25)
                        pdf.set_font("Arial", 'I', 8)
                        pdf.set_text_color(120, 120, 120)
                        pdf.cell(0, 5, "Rapport technique automatisé TPR - Direction Maintenance et Travaux Neufs", 0, 1, 'C')

                        pdf_output = bytes(pdf.output())
                        
                    st.success("✅ Le rapport PDF a été généré avec succès !")
                    st.download_button(
                        label="📥 Télécharger le fichier PDF",
                        data=pdf_output,
                        file_name=f"Rapport_Incidents_TPR_{datetime.now().strftime('%d_%m_%Y')}.pdf",
                        mime="application/pdf"
                    )
        else:
            st.info("Aucune donnée disponible pour cette période ou aucune presse cochée.")
    else:
        st.info("Enregistrez des données pour voir les graphiques.")

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
