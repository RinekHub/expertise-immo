import streamlit as st
import os
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- STYLE CSS POUR LES SOUS-PAVÉS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .section-box { padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE DE L'APPLICATION ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    type_fiche = st.radio("Type de Bien", ["Appt", "Maison"])
    st.markdown("---")
    menu = st.radio("Navigation", ["Dossier Expertise", "Photos & Docs"])

st.title(f"📋 Expertise {type_fiche}")

if menu == "Dossier Expertise":
    # 1. IDENTIFICATION (Commun)
    with st.container():
        st.subheader("👤 1. Identification")
        c1, c2 = st.columns(2)
        with c1:
            donneur = st.text_input("Donneur d'ordre")
            adresse = st.text_input("Adresse du bien")
        with c2:
            proprio = st.text_input("Propriétaire")
            ville = st.text_input("Ville / CP")

    # 2. SECTION IMMEUBLE & SYNDIC (Modif 2a & 3)
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("🏢 2. Caractéristiques de l'Immeuble")
    col_imm1, col_imm2 = st.columns(2)
    with col_imm1:
        st.write("**Bâti**")
        facteur_annee = st.text_input("Facteur Année (Construction/Rénovation)")
        nb_etages = st.text_input("Nombre d'étages")
    with col_imm2:
        st.write("**Gestion Syndic**")
        nom_syndic = st.text_input("Nom du Syndic")
        contact_syndic = st.text_input("Contact / Tél Syndic")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2b. PARTIES COMMUNES (Modif 2b)
    st.subheader("🌳 3. Parties Communes")
    etat_pc = st.selectbox("Niveau d'état général", ["Bon standing", "Standing moyen", "Faible qualité", "Vétuste"])
    sous_criteres_pc = st.multiselect("Sous-critères Parties Communes", 
                                     ["Ascenseur", "Interphone", "Vidéophone", "Espaces verts", "Gardien", "Piscine", "Tennis", "Local vélo"])

    # 4, 5, 6. CARACTÉRISTIQUES TECHNIQUES (Modif 4a, 4b, 5, 6)
    st.subheader("🛠️ 4. Caractéristiques Techniques")
    t1, t2 = st.columns(2)
    with t1:
        # Menuiseries
        etat_menuis = st.selectbox("État des menuiseries", ["Bon état", "Moyen", "Vétuste"])
        type_vitrage = st.multiselect("Type de vitrage", ["Simple vitrage", "Double vitrage", "Double vitrage phonique", "Triple vitrage", "Survitrage"])
        
        # Chauffage & Énergie
        energie = st.selectbox("Énergie Chauffage", ["Gaz", "Électricité", "Fuel", "Pompe à chaleur", "Urbain"])
        distrib_chauffage = st.selectbox("Distribution Chauffage", ["Radiateurs", "Plancher chauffant", "Clim réversible", "Convecteurs"])

    with t2:
        # Eau Chaude
        type_eau_chaude = st.selectbox("Production Eau Chaude", ["Individuelle", "Collective"])
        source_eau_chaude = st.selectbox("Sous-critères Eau Chaude", ["Chaudière Gaz", "Ballon électrique (Cumulus)", "Chauffage Distribution", "Solaire", "Thermodynamique"])
        
        # Situation Locative (Modif 7)
        sit_locative = st.selectbox("Situation Locative", ["Libre de toute occupation", "Occupé (Bail 3/6/9)", "Meublé", "Loyer réglementé", "Saisonnier"])
        details_loc = st.text_input("Précisions (Loyer, échéance...)")

    # 8. ANNEXES (Modif 8)
    st.subheader("📦 5. Annexes")
    annexes_choix = st.multiselect("Type d'annexes", ["Cave", "Box", "Parking extérieur", "Parking sous-sol", "Chambre de bonne", "Grenier", "Terrasse / Balcon"])

    # 9. COMMENTAIRE LIBRE (Modif 9)
    st.subheader("📝 6. Observations libres")
    commentaires = st.text_area("Saisissez vos notes d'expert ici...")

    # 1. TABLEAU DES SURFACES (Modif 1 - Placé à la fin)
    st.markdown("---")
    st.subheader("📏 7. Tableau des Surfaces (Fin de formulaire)")
    if 'rows' not in st.session_state:
        st.session_state.rows = 4

    def add_row(): st.session_state.rows += 1

    for i in range(st.session_state.rows):
        c1, c2, c3 = st.columns([2, 1, 2])
        with c1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
        with c2: st.number_input("m²", key=f"m{i}", step=0.01)
        with c3: st.text_input("Revêtement/Remarques", key=f"r{i}")
    
    st.button("➕ Ajouter une pièce", on_click=add_row)

    # BOUTON GENERATION
    if st.button("💾 Générer le PDF Final"):
        st.success("PDF en cours de création avec toutes les nouvelles sections...")

# 10. INSERTION PHOTO OU DOCUMENT (Modif 10)
elif menu == "Photos & Docs":
    st.subheader("📸 Insertion de documents et photos")
    uploaded_files = st.file_uploader("Glissez vos photos ou documents ici (Plan, DPE, Photos façades...)", 
                                    accept_multiple_files=True, 
                                    type=['png', 'jpg', 'jpeg', 'pdf'])
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            st.write(f"✅ Fichier prêt : {uploaded_file.name}")
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, width=200)