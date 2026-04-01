import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- COMPRESSION PHOTO ---
def process_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        image.thumbnail((800, 800))
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=70)
        return img_byte_arr.getvalue()
    except: return None

# --- INITIALISATION ---
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 3

# --- BARRE LATÉRALE (VÉRIFIEZ BIEN CES 5 OPTIONS) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    type_fiche = st.radio("Type de Bien", ["Appartement", "Maison"])
    st.markdown("---")
    menu = st.radio("Navigation", [
        "1. Dossier & Technique", 
        "2. Extérieurs & Risques", 
        "3. Pathologies", 
        "4. Photos & Signature", 
        "5. Facturation TTC"
    ])

st.title(f"📋 {menu}")

# --- 1. DOSSIER & TECHNIQUE ---
if menu == "1. Dossier & Technique":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Identification")
        st.text_input("Donneur d'ordre")
        addr = st.text_input("Adresse du bien")
        if addr:
            st.markdown(f"📍 [Ouvrir dans Google Maps](https://www.google.com/maps/search/{addr.replace(' ', '+')})")
    with col2:
        st.subheader("🏢 Caractéristiques")
        st.text_input("Année de construction")
        if type_fiche == "Maison":
            st.radio("En copropriété ?", ["Non", "Oui"], horizontal=True)
        else:
            st.text_input("Nom du Syndic")

    st.markdown("---")
    st.subheader("🛠️ Technique & Énergie")
    t1, t2 = st.columns(2)
    with t1:
        st.multiselect("Matériaux", ["PVC", "Alu", "Bois"], key="mat")
        st.selectbox("Chauffage", ["Gaz", "Élec", "Fuel", "PAC", "Bois"])
    with t2:
        st.selectbox("Eau Chaude", ["Cumulus", "Chaudière", "Solaire", "Thermo"])
        st.selectbox("Situation", ["Libre", "Occupé", "Meublé"])

# --- 2. EXTÉRIEURS & RISQUES (ERP) ---
elif menu == "2. Extérieurs & Risques":
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
        st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"])
        st.selectbox("Argiles", ["Nul", "Faible", "Moyen", "Fort"])
    with r2:
        st.checkbox("Zone Inondable")
        st.checkbox("Risque Radon")

# --- 3. PATHOLOGIES ---
elif menu == "3. Pathologies":
    st.subheader("⚠️ Désordres")
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "Faible"})
    
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            st.text_input("Localisation", key=f"l_{idx}")
            st.selectbox("Type", ["Fissure", "Humidité", "Vétusté", "Termites"], key=f"t_{idx}")
            st.select_slider("Gravité", options=["🟢", "🟡", "🔴"], key=f"g_{idx}")
            st.text_area("Observations", key=f"o_{idx}")

# --- 4. PHOTOS & SIGNATURE ---
elif menu == "4. Photos & Signature":
    st.subheader("📸 Photos")
    st.file_uploader("Prendre des photos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
    st.markdown("---")
    st.subheader("✍️ Signature")
    st.text_input("Nom du signataire")
    st.info("Utilisez l'appareil photo pour photographier une signature papier si besoin.")

# --- 5. FACTURATION TTC (MODIFIÉ) ---
elif menu == "5. Facturation TTC":
    st.subheader("💰 Calcul des Honoraires TTC")
    f1, f2 = st.columns(2)
    with f1:
        hono_ttc = st.number_input("Montant de l'Expertise TTC (€)", value=0.0)
        km = st.number_input("Distance parcourue (km)", value=0)
    with f2:
        tarif_km_ttc = st.number_input("Tarif Kilométrique TTC (€/km)", value=0.60)
        frais_ttc = st.number_input("Autres frais TTC (€)", value=0.0)
    
    total_ik_ttc = km * tarif_km_ttc
    grand_total_ttc = hono_ttc + total_ik_ttc + frais_ttc
    
    st.markdown("---")
    st.metric("Total Indemnités Kilométriques TTC", f"{total_ik_ttc:.2f} €")
    st.metric("TOTAL GÉNÉRAL TTC", f"{grand_total_ttc:.2f} €", delta_color="normal")
    
    st.write(f"*(Soit {grand_total_ttc/1.2:.2f} € Hors Taxes)*")

st.markdown("---")
if st.button("💾 ENREGISTRER TOUT"):
    st.balloons()