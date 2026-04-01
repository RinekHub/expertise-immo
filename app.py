import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- FONCTION DE COMPRESSION ---
def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    image.thumbnail((800, 800))
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', quality=70)
    return img_byte_arr.getvalue()

# --- INTERFACE BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    type_fiche = st.radio("Type de Bien", ["Appartement", "Maison"])
    st.markdown("---")
    menu = st.radio("Navigation", ["Dossier Expertise", "Photos & Docs", "Pathologies & Facture"])

st.title(f"📋 Expertise {type_fiche}")

if menu == "Dossier Expertise":
    # 1. Identification
    st.subheader("👤 1. Identification")
    c1, c2 = st.columns(2)
    with c1:
        donneur = st.text_input("Donneur d'ordre")
        adresse = st.text_input("Adresse du bien")
    with c2:
        proprio = st.text_input("Propriétaire")
        ville = st.text_input("Ville / CP")

    # 2. Immeuble / Maison & Gestion (MODIFIÉ)
    st.markdown("---")
    st.subheader(f"🏠 2. Caractéristiques {type_fiche}")
    ci1, ci2 = st.columns(2)
    with ci1:
        facteur_annee = st.text_input("Facteur Année (Construction/Rénovation)")
        nb_etages = st.text_input("Nombre d'étages / Niveaux")
    with ci2:
        if type_fiche == "Appartement":
            nom_syndic = st.text_input("Nom du Syndic")
            contact_syndic = st.text_input("Contact Syndic")
        else:
            is_copro = st.radio("La maison est-elle en copropriété ?", ["Non", "Oui"], horizontal=True)
            if is_copro == "Oui":
                nom_syndic_maison = st.text_input("Nom du Syndic / Association")
                charges_maison = st.text_input("Montant des charges annuelles")

    # 3. Parties Communes / Extérieurs
    st.subheader(f"🌳 3. État des {'parties communes' if type_fiche == 'Appartement' else 'extérieurs'}")
    etat_pc = st.selectbox("Niveau d'état général", ["Bon standing", "Standing moyen", "Faible qualité", "Vétuste"])
    if type_fiche == "Appartement":
        sous_criteres_pc = st.multiselect("Sous-critères", ["Ascenseur", "Interphone", "Espaces verts", "Gardien", "Local vélo"], placeholder="Sélectionnez les équipements")
    else:
        sous_criteres_pc = st.multiselect("Sous-critères Maison", ["Clôture", "Portail électrique", "Piscine", "Dépendance", "Jardin"], placeholder="Sélectionnez les équipements")

    # 4. Technique
    st.markdown("---")
    st.subheader("🛠️ 4. Caractéristiques Techniques")
    t1, t2 = st.columns(2)
    
    with t1:
        etat_menuis = st.selectbox("État des menuiseries", ["Bon état", "Moyen", "Vétuste"])
        type_vitrage = st.multiselect("Type de vitrage & Matériaux", [
            "PVC Simple vitrage", "PVC Double vitrage", "Aluminium", "Bois", "Double vitrage phonique", "Triple vitrage"
        ], placeholder="Choisir les types")
        
        energie = st.selectbox("Énergie Chauffage", ["Gaz", "Électricité", "Fuel", "Chaudière électrique", "Pompe à chaleur", "Bois/Granulés"])
        distrib = st.selectbox("Distribution", ["Radiateurs", "Plancher chauffant", "Clim réversible", "Convecteurs"])

    with t2:
        if type_fiche == "Appartement":
            eau_type = st.selectbox("Production Eau Chaude", ["Individuelle", "Collective"])
            eau_source = st.selectbox("Source Eau Chaude", ["Chaudière Gaz", "Cumulus Élec", "Chauffage Distri"])
        else:
            eau_source = st.selectbox("Production Eau Chaude", ["Chaudière Gaz", "Ballon électrique (Cumulus)", "Thermodynamique", "Solaire"])
        
        sit_loc = st.selectbox("Situation Locative", ["Libre", "Occupé (Bail)", "Meublé", "Saisonnier"])

    # 5. Annexes & Commentaires
    st.subheader("📦 5. Annexes & Notes")
    annexes = st.multiselect("Annexes", ["Cave", "Box", "Garage", "Terrasse", "Grenier", "Abri de jardin"], placeholder="Choisir une ou plusieurs options")
    commentaires = st.text_area("Zone de commentaire libre")

    # 6. Tableau des Surfaces
    st.markdown("---")
    st.subheader("📏 6. Tableau des Surfaces")
    if 'rows' not in st.session_state: st.session_state.rows = 4
    for i in range(st.session_state.rows):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
        with sc2: st.number_input("m²", key=f"m{i}", step=0.01)
        with sc3: st.text_input("Notes", key=f"r{i}")
    st.button("➕ Ajouter une pièce", on_click=lambda: st.session_state.update({"rows": st.session_state.rows + 1}))

elif menu == "Photos & Docs":
    st.subheader("📸 Insertion de documents et photos")
    uploaded_files = st.file_uploader("Prendre une photo", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    if uploaded_files:
        cols = st.columns(3)
        for idx, f in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.image(f, use_container_width=True)

st.markdown("---")
if st.button("💾 GÉNÉRER LE RAPPORT PDF FINAL"):
    st.balloons()
    st.success("Données enregistrées.")