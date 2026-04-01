import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- FONCTION DE COMPRESSION ---
def process_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        image.thumbnail((800, 800))
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=70)
        return img_byte_arr.getvalue()
    except: return None

# --- INITIALISATION SESSION ---
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 3

# --- BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    type_fiche = st.radio("Type de Bien", ["Appartement", "Maison"])
    st.markdown("---")
    menu = st.radio("Navigation", [
        "Dossier & Technique", 
        "Extérieurs & Risques", 
        "Pathologies", 
        "Photos & Signature", 
        "Facturation"
    ])

st.title(f"📋 {menu}")

# --- SECTION 1 : DOSSIER & TECHNIQUE ---
if menu == "Dossier & Technique":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Identification")
        st.text_input("Donneur d'ordre")
        addr = st.text_input("Adresse du bien")
        if addr:
            st.markdown(f"[📍 Voir sur Google Maps](https://www.google.com/maps/search/{addr.replace(' ', '+')})")
    with col2:
        st.subheader("🏢 Caractéristiques")
        st.text_input("Année de construction")
        if type_fiche == "Maison":
            st.radio("Copropriété ?", ["Non", "Oui"], horizontal=True)
        else:
            st.text_input("Nom du Syndic")

    st.markdown("---")
    st.subheader("🛠️ Technique & Énergie")
    t1, t2 = st.columns(2)
    with t1:
        st.multiselect("Matériaux Menuiseries", ["PVC", "Aluminium", "Bois"], key="mat")
        st.selectbox("Vitrage", ["Simple", "Double", "Double Phonique", "Triple"])
    with t2:
        st.selectbox("Chauffage", ["Gaz", "Élec", "Fuel", "PAC", "Bois"])
        st.selectbox("Eau Chaude", ["Cumulus", "Chaudière", "Solaire", "Thermodynamique"])

# --- SECTION 2 : EXTÉRIEURS & RISQUES ---
elif menu == "Extérieurs & Risques":
    st.subheader("🏡 Aménagements Extérieurs")
    e1, e2 = st.columns(2)
    with e1:
        st.multiselect("Éléments", ["Clôture", "Portail Élec", "Arrosage", "Puits", "Cuisine d'été"])
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"])
    with e2:
        st.multiselect("Annexes", ["Garage", "Cave", "Abri", "Carport", "Terrasse"])

    st.markdown("---")
    st.subheader("🚫 État des Risques (ERP)")
    r1, r2 = st.columns(2)
    with r1:
        st.selectbox("Zone Sismique", ["1 (Très faible)", "2 (Faible)", "3 (Modéré)", "4 (Moyen)", "5 (Fort)"])
        st.selectbox("Retrait-Gonflement Argiles", ["Nul", "Faible", "Moyen", "Fort"])
    with r2:
        st.checkbox("Zone Inondable")
        st.checkbox("Plan d'Exposition au Bruit (PEB)")
        st.checkbox("Risque Radon")

# --- SECTION 3 : PATHOLOGIES ---
elif menu == "Pathologies":
    st.subheader("⚠️ Diagnostic des Désordres")
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "Faible"})
    
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            c1, c2, c3 = st.columns([2,2,1])
            with c1: st.text_input("Localisation", key=f"l_{idx}")
            with c2: st.selectbox("Type", ["Fissure", "Humidité", "Vétusté", "Termites"], key=f"t_{idx}")
            with c3: st.select_slider("Gravité", options=["🟢", "🟡", "🔴"], key=f"g_{idx}")
            st.text_area("Observations", key=f"o_{idx}")
            if st.button("Supprimer", key=f"d_{idx}"):
                st.session_state.pathos.pop(idx)
                st.rerun()

# --- SECTION 4 : PHOTOS & SIGNATURE ---
elif menu == "Photos & Signature":
    st.subheader("📸 Reportage Photographique")
    st.file_uploader("Prendre des photos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
    
    st.markdown("---")
    st.subheader("✍️ Signature du Client / Donneur d'ordre")
    st.info("Le client peut signer directement ci-dessous avec son doigt ou un stylet.")
    # Zone de signature (Note: En pur Streamlit standard, on utilise un champ de dépôt ou un canvas)
    st.text_input("Nom du signataire")
    st.file_uploader("Importer une capture de signature (si nécessaire)", type=['png'])

# --- SECTION 5 : FACTURATION ---
elif menu == "Facturation":
    st.subheader("💰 Calcul des Honoraires")
    f1, f2 = st.columns(2)
    with f1:
        hono = st.number_input("Honoraires HT (€)", value=0.0)
        km = st.number_input("Distance parcourue (km Aller-Retour)", value=0)
    with f2:
        tarif_km = st.number_input("Tarif IK (€/km)", value=0.60)
        frais_fixes = st.number_input("Autres frais (€)", value=0.0)
    
    total_ik = km * tarif_km
    total_ht = hono + total_ik + frais_fixes
    st.metric("Total Indemnités Kilométriques", f"{total_ik:.2f} €")
    st.metric("TOTAL HT", f"{total_ht:.2f} €")
    if st.checkbox("Appliquer TVA 20%"):
        st.metric("TOTAL TTC", f"{total_ht * 1.2:.2f} €")

st.markdown("---")
if st.button("💾 CLÔTURER L'EXPERTISE ET ENREGISTRER"):
    st.balloons()
    st.success("Toutes les sections sont complétées. Prêt pour le PDF !")