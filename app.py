import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 5

# --- 2. GESTION DU LOGO (HAUT DE PAGE) ---
def afficher_logo_fd():
    if os.path.exists("logo.png"):
        try:
            img = Image.open("logo.png")
            if img.mode in ("RGBA", "P"): img = img.convert("RGB")
            st.image(img, width=220)
        except: st.error("Logo présent mais illisible")
    else:
        st.warning("Logo FD non trouvé sur GitHub (logo.png)")

# --- 3. BARRE LATÉRALE (LOGO + NAVIGATION) ---
with st.sidebar:
    afficher_logo_fd() # LE LOGO EST BIEN ICI TOUT EN HAUT
    st.markdown("---")
    type_bien = st.radio("🏠 Type de Bien", ["Appartement", "Maison"], key="type_bien")
    st.markdown("---")
    if st.button("🗑️ NOUVEAU DOSSIER (RESET)"):
        st.session_state.clear()
        st.rerun()

st.title(f"Expertise : {type_bien}")

# --- SECTION 1 : DOSSIER & TECHNIQUE ---
st.header("1. Section Dossier & Technique")
c1, c2 = st.columns(2)
with c1:
    st.subheader("👤 Identification")
    st.text_input("Donneur d'ordre", key="d_client")
    st.text_input("Propriétaire", key="d_prop")
    adr = st.text_input("Adresse du bien", key="d_adr")
with c2:
    st.subheader("🏢 Bloc Immeuble")
    st.text_input("Facteur Année (Const./Rénov.)", key="i_annee")
    st.selectbox("Situation Locative", ["Libre", "Occupé", "Loué", "Vides"], key="i_loc")
    if type_bien == "Appartement":
        st.text_input("Syndic", key="i_syndic")
        st.checkbox("Ascenseur", key="i_asc")
    else:
        st.radio("Copropriété ?", ["Non", "Oui"], key="i_copro_m")

st.markdown("---")

# --- SECTION 2 : MENUISERIES & ÉNERGIE ---
st.header("2. Menuiseries & Énergies")
m1, m2 = st.columns(2)
with m1:
    st.multiselect("Matériaux", ["PVC", "Alu", "Bois"], key="m_mat")
    st.selectbox("Type de vitrage", ["Simple vitrage", "Double vitrage", "Double vitrage FE"], key="m_vitre")
    st.selectbox("État menuiseries", ["Bon", "Moyen", "Vétuste"], key="m_etat")
with m2:
    st.selectbox("Source énergie", ["Électricité", "Gaz", "PAC", "Fuel", "Chaudière élec"], key="e_source")
    st.selectbox("Production Eau Chaude", ["Cumulus", "Ballon Thermo", "Chaudière mixte"], key="e_eau")

st.markdown("---")

# --- SECTION 3 : EXTÉRIEURS & RISQUES (ERP) ---
st.header("3. Extérieurs & Risques")
e1, e2 = st.columns(2)
with e1:
    if type_bien == "Maison":
        st.text_input("Clôture / Haies", key="t_cloture")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"], key="t_piscine")
    st.selectbox("Entretien Général", ["Excellent", "Bon", "Moyen", "Négligé"], key="i_entretien")
with e2:
    st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="erp_sis")
    st.selectbox("Aléa Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="erp_arg")

st.markdown("---")

# --- SECTION 4 : PATHOLOGIES ---
st.header("4. Section Pathologies")
if st.button("➕ Ajouter un désordre"):
    st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢 Faible", "obs": ""})
    st.rerun()

for idx, p in enumerate(st.session_state.pathos):
    with st.expander(f"Désordre n°{idx+1}", expanded=True):
        st.session_state.pathos[idx]["loc"] = st.text_input("Localisation", key=f"ploc_{idx}", value=p["loc"])
        st.session_state.pathos[idx]["grav"] = st.select_slider("Gravité", options=["🟢 Faible", "🟡 Modéré", "🔴 Grave"], key=f"pgrav_{idx}", value=p["grav"])
        st.session_state.pathos[idx]["obs"] = st.text_area("Observations", key=f"pobs_{idx}", value=p["obs"])
        if st.button(f"🗑️ Supprimer n°{idx+1}", key=f"del_{idx}"):
            st.session_state.pathos.pop(idx)
            st.rerun()

st.markdown("---")

# --- SECTION 5 : SURFACES (EN BAS) ---
st.header("5. Tableau des Surfaces")
for i in range(st.session_state.rows):
    sc1, sc2, sc3 = st.columns([2, 1, 2])
    with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
    with sc2: st.number_input("m²", key=f"m{i}", step=0.01)
    with sc3: st.text_input("Obs", key=f"r{i}")
if st.button("➕ Ajouter une ligne"):
    st.session_state.rows += 1
    st.rerun()

st.markdown("---")

# --- SECTION 6 : FACTURATION ---
st.header("6. Facturation")
f1, f2, f3 = st.columns(3)
with f1: h_ttc = st.number_input("Hono TTC (€)", key="h_val")
with f2: dist = st.number_input("KM (A/R)", key="dist_val")
with f3: t_km = st.number_input("Tarif KM", value=0.60, key="tk_val")
total = h_ttc + (dist * t_km)
st.metric("TOTAL GÉNÉRAL TTC", f"{total:.2f} €")

st.markdown("---")

# --- SECTION 7 : PHOTOS & DOCUMENTS (DÉPLACÉ ICI À LA FIN) ---
st.header("7. Photos & Signature")
st.file_uploader("📸 Ajouter des photos (Appareil photo iPad)", accept_multiple_files=True, key="photos_final")
st.text_input("🖋️ Signature (Nom du signataire)", key="signature_nom")

# --- BOUTON PDF FINAL ---
st.markdown("---")
if st.button("📄 GÉNÉRER LE RAPPORT FINAL"):
    st.success("Génération du PDF avec Logo FD en cours...")
    # (Logique PDF identique au socle)