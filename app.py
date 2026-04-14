import streamlit as st

st.set_page_config(page_title="Calculateur Extrusion TPR", page_icon="📟", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        header { visibility: visible !important; height: 60px !important; }
        .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; }
        
        /* Style des barres de visualisation */
        .container-barre { width: 100%; background-color: #e0e0e0; border-radius: 5px; height: 20px; position: relative;}
        .barre-lopin { background-color: #808080; height: 100%; border-radius: 5px; transition: width 0.5s;}
        .barre-limite { background-color: #1a4332; height: 8px; border-radius: 5px; margin-top: 4px;}
        
        /* Style Section Rappel Température */
        .temp-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #0047AB;
            margin-bottom: 20px;
        }

        /* Bouton Calculer */
        div.stButton > button {
            width: 100%; height: 3em; border-radius: 12px;
            background: linear-gradient(135deg, #0047AB 0%, #00264d 100%);
            color: white !important; font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(0, 71, 171, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)

CONFIG_PRESSES = {
    "Presse 4": {"diametre": 228, "limite_longueur": 1150},
    "Presse 6": {"diametre": 178, "limite_longueur": 890},
    "Presse 7": {"diametre": 178, "limite_longueur": 1000},
}

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    presse_choisie = st.selectbox("Sélectionnez la Presse :", options=list(CONFIG_PRESSES.keys()), index=None)
    
    st.divider()
    st.markdown("### 🌡️ Rappel Températures")
    st.info("""
    **Conteneur:** 400-430°C (+/-10)
    **Filière:** 450°C (+/-10)
    **Lopin (Plate):** 440-470°C
    **Lopin (Tubul):** 470-510°C
    """)

# --- HEADER ---
col_logo, col_titre = st.columns([1, 4])
with col_logo:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6q1BtDSDgVnJZFo0hOBfQJoDS6OYiub-qfQ&s", width=120)

with col_titre:
    st.markdown("<h2 style='margin: 0;'>Tunisie Profilés d'Aluminium</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='margin: 0; color: #555;'>Suivi Production & Calcul d'Extrusion</h4>", unsafe_allow_html=True)

if not presse_choisie:
    st.warning("👈 Veuillez choisir une presse dans le menu à gauche pour commencer.")
    st.stop()

# --- ONGLETS POUR SEPARER CALCUL ET FORMULAIRE ---
tab1, tab2 = st.tabs(["🧮 Calculateur de Lopin", "📝 Déclaration Arrêt (Chapeau)"])

# --- ONGLET 1 : CALCULATEUR ---
with tab1:
    st.subheader(f"Calcul de l'optimum - {presse_choisie}")
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        type_billette = st.selectbox("Nature de la billette :", ["Primaire", "Recyclée"])
        p_m = st.number_input("P/m du profilé (kg/m)", format="%.3f", key="pm_calc")
    with col_in2:
        n_ecoulements = st.number_input("Nombre d'écoulements", min_value=1, step=1, key="ne_calc")
        long_demandee = st.number_input("Longueur demandée (m)", format="%.2f", key="ld_calc")

    if st.button("CALCULER"):
        if p_m and long_demandee:
            poids_lineique = 110.180
            diam = CONFIG_PRESSES[presse_choisie]["diametre"]
            k = 0.1 if type_billette == "Primaire" else 0.16
            
            long_culot = k * diam
            poids_lopin = ((p_m * n_ecoulements) * long_demandee) + (poids_lineique * (long_culot / 1000))
            long_lopin_mm = (poids_lopin / poids_lineique) * 1000
            
            if long_lopin_mm > CONFIG_PRESSES[presse_choisie]["limite_longueur"]:
                st.error(f"🚨 LOPIN TROP LONG : {long_lopin_mm:.0f} mm (Max: {CONFIG_PRESSES[presse_choisie]['limite_longueur']} mm)")
            else:
                st.success(f"✅ Longueur Lopin : {long_lopin_mm:.1f} mm | Culot : {long_culot:.1f} mm")
                st.metric("Poids total lopin", f"{poids_lopin:.2f} kg")

# --- ONGLET 2 : FORMULAIRE D'ARRÊT ---
with tab2:
    st.subheader("⚠️ Signalement Problème Chapeau / Arrêt")
    
    with st.expander("📌 Aide à l'identification (Nomenclature)"):
        st.write("""
        - **M** : Matière (Lopin mal coupé, température, calamine)
        - **R** : Réglage (Pression, alignement, vitesse)
        - **O** : Outillage (Chapeau fissuré, vis cassée, usure)
        - **L** : Lubrification (Collage, buse bouchée)
        - **A** : Autre (Préciser en commentaire)
        """)

    with st.form("form_arret"):
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            poste = st.radio("Poste :", ["A", "B", "C"], horizontal=True)
            ref_filiere = st.text_input("Réf Filière :")
        with col_f2:
            num_lopin = st.text_input("Numéro du Lopin :")
            duree_arret = st.number_input("Durée d'arrêt (min) :", min_value=0)
        with col_f3:
            cause_code = st.selectbox("Cause possible (Code) :", ["M", "R", "O", "L", "A"])
            
        commentaire = st.text_area("Observations additionnelles :")
        
        # Le bouton de soumission du formulaire
        submitted = st.form_submit_button("ENREGISTRER L'ARRÊT")
        
        if submitted:
            if ref_filiere and num_lopin:
                st.success(f"Enregistré : Arrêt de {duree_arret} min sur {presse_choisie} (Code {cause_code})")
                # Ici, on pourrait ajouter le code pour envoyer vers Excel/Google Sheets
            else:
                st.error("Veuillez remplir au moins la Réf Filière et le Numéro du Lopin.")

# --- FOOTER ---
st.markdown(f"""
    <div class="temp-card">
        <strong>💡 Rappel de sécurité :</strong> En cas de code <b>O (Outillage)</b>, 
        informer immédiatement le chef de poste pour vérification du chapeau.
    </div>
    <div style="text-align: center; color: gray; font-size: 0.8em;">
        © 2026 TPR | Direction Maintenance et Travaux Neufs
    </div>
    """, unsafe_allow_html=True)
