import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Suivi Arrêts TPR", page_icon="📝", layout="centered")

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
        .main { background-color: #f5f7f9; }
        .stButton > button {
            width: 100%; height: 3.5em; border-radius: 10px;
            background: linear-gradient(135deg, #d32f2f 0%, #8b0000 100%);
            color: white !important; font-weight: bold;
            border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .temp-box {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        .highlight { color: #0047AB; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_titre = st.columns([1, 3])
with col_logo:
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6q1BtDSDgVnJZFo0hOBfQJoDS6OYiub-qfQ&s", width=100)

with col_titre:
    st.title("Signalement Arrêt Production")
    st.write("Direction Maintenance et Travaux Neufs - TPR")

st.divider()

# --- SECTION RAPPEL TEMPÉRATURES ---
with st.expander("🌡️ VOIR LES STANDARDS DE TEMPÉRATURE (RAPPEL)", expanded=False):
    st.markdown("""
    <div class="temp-box">
        <p>• <b>Conteneur :</b> 400°C à 430°C <span class="highlight">(+/- 10°C)</span></p>
        <p>• <b>Filière :</b> 450°C <span class="highlight">(+/- 10°C)</span></p>
        <p>• <b>Lopin (Filière Plate) :</b> 440°C à 470°C <span class="highlight">(+/- 10°C)</span></p>
        <p>• <b>Lopin (Filière Tubulaire) :</b> 470°C à 510°C <span class="highlight">(+/- 10°C)</span></p>
    </div>
    """, unsafe_allow_html=True)

# --- FORMULAIRE DE SAISIE ---
st.subheader("📝 Formulaire de diagnostic")

with st.form("diagnostic_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        date_arret = st.date_input("Date", datetime.now())
        poste = st.radio("Poste", ["A", "B", "C"], horizontal=True)
        ref_filiere = st.text_input("Référence Filière", placeholder="Ex: F1234")
    
    with col2:
        num_lopin = st.text_input("Numéro du lopin", placeholder="Ex: 450")
        duree = st.number_input("Durée d'arrêt (minutes)", min_value=0, step=5)
        cause = st.selectbox("Cause possible (Nomenclature)", [
            "M - Matière (Lopin, Coupe, Température)",
            "R - Réglage (Pression, Alignement, Vitesse)",
            "O - Outillage (Chapeau, Casse, Usure)",
            "L - Lubrification (Collage, Buse bouchée)",
            "A - Autre (Préciser ci-dessous)"
        ])

    commentaire = st.text_area("Observations additionnelles (Optionnel)", placeholder="Décrivez le problème ici...")
    
    submit_button = st.form_submit_button("ENREGISTRER L'ARRÊT")

# --- LOGIQUE APRÈS SOUMISSION ---
if submit_button:
    if not ref_filiere or not num_lopin:
        st.error("❌ Erreur : Veuillez remplir la 'Référence Filière' et le 'Numéro de lopin'.")
    else:
        # Ici vous pouvez ajouter le code pour enregistrer dans une base de données ou un Excel
        st.success(f"✅ Arrêt enregistré avec succès pour la filière {ref_filiere} (Poste {poste})")
        st.balloons()

# --- FOOTER ---
st.markdown("---")
st.caption("Système d'aide à l'identification des pannes - 2026 TPR")
