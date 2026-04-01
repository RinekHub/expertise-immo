import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- INITIALISATION DES PATHOLOGIES ---
if 'pathos' not in st.session_state:
    st.session_state.pathos = [{"loc": "", "type": "Fissure", "grav": "Faible", "obs": ""}]

def add_patho():
    st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "Faible", "obs": ""})

# --- INTERFACE BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    type_fiche = st.radio("Type de Bien", ["Appartement", "Maison"])
    st.markdown("---")
    menu = st.radio("Navigation", ["Dossier Expertise", "Pathologies & Désordres", "Photos & Docs", "Facturation"])

st.title(f"📋 {menu} - {type_fiche}")

# --- ONGLET 1 : DOSSIER EXPERTISE (Le formulaire précédent) ---
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
        facteur_annee = st.text_input("Facteur Année")
        nb_etages = st.text_input("Nombre d'étages / Niveaux")
    with ci2:
        if type_fiche == "Appartement":
            nom_syndic = st.text_input("Nom du Syndic")
        else:
            is_copro = st.radio("La maison est-elle en copropriété ?", ["Non", "Oui"], horizontal=True)
            if is_copro == "Oui":
                st.text_input("Nom du Syndic / Association")

    st.markdown("---")
    st.subheader("📏 3. Tableau des Surfaces")
    if 'rows' not in st.session_state: st.session_state.rows = 3
    for i in range(st.session_state.rows):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
        with sc2: st.number_input("m²", key=f"m{i}", step=0.01)
        with sc3: st.text_input("Notes", key=f"r{i}")
    st.button("➕ Ajouter une pièce", on_click=lambda: st.session_state.update({"rows": st.session_state.rows + 1}))

# --- ONGLET 2 : PATHOLOGIES (NOUVEAU FORMULAIRE DÉTAILLÉ) ---
elif menu == "Pathologies & Désordres":
    st.subheader("⚠️ Relevé des Pathologies du Bâtiment")
    st.info("Détaillez ici chaque désordre observé lors de la visite.")

    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1} : {p['type']} - {p['loc']}", expanded=True):
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.session_state.pathos[idx]["loc"] = st.text_input(f"Localisation", key=f"loc_{idx}", placeholder="Ex: Façade Nord, Sous-sol...")
            with c2:
                st.session_state.pathos[idx]["type"] = st.selectbox(f"Type de pathologie", 
                    ["Fissure structurelle", "Fissure de retrait", "Humidité / Salpêtre", "Infiltration toiture", "Remontée capillaire", "Termites / Parasites", "Vétusté réseaux", "Autre"], key=f"type_{idx}")
            with c3:
                st.session_state.pathos[idx]["grav"] = st.select_slider(f"Gravité", options=["Faible", "Moyenne", "Critique"], key=f"grav_{idx}")
            
            st.session_state.pathos[idx]["obs"] = st.text_area(f"Observations et Préconisations", key=f"obs_{idx}", placeholder="Décrivez le désordre et les travaux conseillés...")
            
            if st.button(f"🗑️ Supprimer le désordre {idx+1}", key=f"del_{idx}"):
                st.session_state.pathos.pop(idx)
                st.rerun()

    st.button("➕ Ajouter un nouveau désordre", on_click=add_patho)

# --- ONGLET 3 : PHOTOS ---
elif menu == "Photos & Docs":
    st.subheader("📸 Photos de l'expertise")
    uploaded_files = st.file_uploader("Prendre une photo", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    if uploaded_files:
        cols = st.columns(3)
        for idx, f in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.image(f, use_container_width=True)

# --- ONGLET 4 : FACTURATION ---
elif menu == "Facturation":
    st.subheader("💰 Honoraires et Frais")
    c1, c2 = st.columns(2)
    with c1:
        hono = st.number_input("Honoraires HT (€)", value=0.0)
        tva = st.checkbox("Appliquer TVA 20%", value=True)
    with c2:
        frais = st.number_input("Frais de déplacement / Annexes (€)", value=0.0)
    
    total_ht = hono + frais
    total_ttc = total_ht * 1.2 if tva else total_ht
    st.metric("TOTAL HT", f"{total_ht:.2f} €")
    st.metric("TOTAL TTC", f"{total_ttc:.2f} €")

st.markdown("---")
if st.button("💾 GÉNÉRER LE RAPPORT FINAL"):
    st.balloons()
    st.success("Rapport compilé !")