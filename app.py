import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- INITIALISATION ---
if 'pathos' not in st.session_state:
    st.session_state.pathos = [{"loc": "", "type": "Fissure structurelle", "grav": "Faible", "obs": ""}]
if 'rows' not in st.session_state:
    st.session_state.rows = 4

def add_patho():
    st.session_state.pathos.append({"loc": "", "type": "Fissure structurelle", "grav": "Faible", "obs": ""})

def add_row():
    st.session_state.rows += 1

# --- BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    type_fiche = st.radio("Type de Bien", ["Appartement", "Maison"])
    st.markdown("---")
    menu = st.radio("Navigation", ["Dossier Expertise", "Pathologies & Désordres", "Photos & Docs", "Facturation"])

st.title(f"📋 {menu} - {type_fiche}")

# --- ONGLET 1 : DOSSIER EXPERTISE ---
if menu == "Dossier Expertise":
    st.subheader("👤 1. Identification")
    c1, c2 = st.columns(2)
    with c1:
        donneur = st.text_input("Donneur d'ordre")
        adresse = st.text_input("Adresse du bien")
    with c2:
        proprio = st.text_input("Propriétaire")
        ville = st.text_input("Ville / CP")

    st.markdown("---")
    st.subheader(f"🏠 2. Caractéristiques {type_fiche}")
    ci1, ci2 = st.columns(2)
    with ci1:
        facteur_annee = st.text_input("Facteur Année (Construction/Rénovation)")
        nb_etages = st.text_input("Nombre d'étages / Niveaux")
    with ci2:
        if type_fiche == "Appartement":
            st.text_input("Nom du Syndic")
            st.text_input("Contact Syndic")
        else:
            is_copro = st.radio("La maison est-elle en copropriété ?", ["Non", "Oui"], horizontal=True)
            if is_copro == "Oui":
                st.text_input("Nom du Syndic / Association")
                st.text_input("Montant des charges annuelles")

    st.subheader(f"🌳 3. État des {'parties communes' if type_fiche == 'Appartement' else 'extérieurs'}")
    st.selectbox("Niveau d'état général", ["Bon standing", "Standing moyen", "Faible qualité", "Vétuste"])
    st.multiselect("Sous-critères", ["Ascenseur", "Portail", "Jardin", "Gardien", "Local vélo"], placeholder="Sélectionnez")

    st.markdown("---")
    st.subheader("🛠️ 4. Caractéristiques Techniques")
    t1, t2 = st.columns(2)
    with t1:
        st.selectbox("État des menuiseries", ["Bon état", "Moyen", "Vétuste"])
        st.multiselect("Vitrages & Matériaux", ["PVC Simple vitrage", "PVC Double vitrage", "Aluminium", "Bois"], placeholder="Choisir")
        st.selectbox("Énergie Chauffage", ["Gaz", "Électricité", "Fuel", "Chaudière électrique", "Pompe à chaleur"])
    with t2:
        if type_fiche == "Appartement":
            st.selectbox("Production Eau Chaude", ["Individuelle", "Collective"])
        else:
            st.selectbox("Production Eau Chaude", ["Chaudière Gaz", "Ballon électrique", "Solaire"])
        st.selectbox("Situation Locative", ["Libre", "Occupé", "Meublé"])

    st.subheader("📦 5. Annexes & Notes")
    st.multiselect("Annexes", ["Cave", "Box", "Garage", "Terrasse"], placeholder="Choisir")
    st.text_area("Zone de commentaire libre")

    st.markdown("---")
    st.subheader("📏 6. Tableau des Surfaces")
    for i in range(st.session_state.rows):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
        with sc2: st.number_input("m²", key=f"m{i}", step=0.01)
        with sc3: st.text_input("Notes", key=f"r{i}")
    st.button("➕ Ajouter une pièce", on_click=add_row)

# --- ONGLET 2 : PATHOLOGIES ---
elif menu == "Pathologies & Désordres":
    st.subheader("⚠️ Relevé des Pathologies")
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.session_state.pathos[idx]["loc"] = st.text_input("Localisation", key=f"loc_{idx}")
            with c2:
                st.session_state.pathos[idx]["type"] = st.selectbox("Type", ["Fissure", "Humidité", "Infiltration", "Vétusté"], key=f"type_{idx}")
            with c3:
                st.session_state.pathos[idx]["grav"] = st.select_slider("Gravité", options=["Faible", "Moyenne", "Critique"], key=f"grav_{idx}")
            st.session_state.pathos[idx]["obs"] = st.text_area("Observations", key=f"obs_{idx}")
    st.button("➕ Ajouter un désordre", on_click=add_patho)

# --- ONGLET 3 : PHOTOS ---
elif menu == "Photos & Docs":
    st.subheader("📸 Photos")
    st.file_uploader("Prendre une photo", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

# --- ONGLET 4 : FACTURATION ---
elif menu == "Facturation":
    st.subheader("💰 Facturation")
    h1, h2 = st.columns(2)
    with h1: st.number_input("Honoraires HT (€)", value=0.0)
    with h2: st.number_input("Frais déplacement (€)", value=0.0)

st.markdown("---")
if st.button("💾 ENREGISTRER L'EXPERTISE"):
    st.balloons()