import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io
import urllib.parse

# --- 1. CONFIGURATION ET COMPRESSION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    
    # --- CORRECTIF : Conversion pour éviter l'erreur JPEG ---
    # Si l'image a une couche de transparence (RGBA) ou est en noir et blanc (P/L), 
    # on la convertit en RGB standard.
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    image.thumbnail((800, 800))
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', quality=70)
    return img_byte_arr.getvalue()

# --- CLASSE PDF MODIFIÉE (SÉCURISÉE POUR LE LOGO) ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            try:
                # On utilise Pillow pour ouvrir et convertir le logo 
                # Cela retire l'entrelacement qui fait planter FPDF
                img = Image.open("logo.png")
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # On sauve temporairement en mémoire pour le PDF
                img_temp = io.BytesIO()
                img.save(img_temp, format='JPEG')
                img_temp.seek(0)
                
                self.image(img_temp, 10, 8, 33, type='JPEG')
            except Exception:
                # Si vraiment le logo pose problème, on écrit le nom du Cabinet
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'FD EXPERTISE', 0, 0, 'L')
                
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE', 0, 1, 'C')
        self.ln(10)

# --- 3. INITIALISATION ---
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 4

# --- 4. BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    type_fiche = st.radio("Type de Bien", ["Appartement", "Maison"])
    st.markdown("---")
    menu = st.radio("Navigation", [
        "1. Dossier Technique", 
        "2. Extérieurs & Risques", 
        "3. Diagnostic Pathologies", 
        "4. Photos & Signature",
        "5. Facturation TTC"
    ])

st.title(f"📋 Expertise {type_fiche}")
txt_choix = "Choisissez une ou plusieurs options"

# --- SECTION 1 : DOSSIER TECHNIQUE ---
if menu == "1. Dossier Technique":
    st.subheader("👤 Identification & Caractéristiques")
    c1, c2 = st.columns(2)
    with c1:
        donneur = st.text_input("Donneur d'ordre", key="d_client")
        adresse = st.text_input("Adresse du bien", key="d_adr")
        if adresse:
            query = urllib.parse.quote(adresse)
            st.markdown(f"[📍 Voir sur Google Maps](https://www.google.com/maps/search/?api=1&query={query})")
    with c2:
        proprio = st.text_input("Propriétaire", key="d_prop")
        ville = st.text_input("Ville / CP", key="d_ville")

    st.markdown("---")
    t1, t2 = st.columns(2)
    with t1:
        facteur_annee = st.text_input("Année (Construction/Rénovation)", key="d_annee")
        nb_etages = st.text_input("Nombre d'étages / Niveaux", key="d_niv")
        st.multiselect("Menuiseries & Vitrage", [
            "PVC Simple vitrage", "PVC Double vitrage", "Aluminium Simple vitrage", 
            "Aluminium Double vitrage", "Bois Simple vitrage", "Bois Double vitrage"
        ], placeholder=txt_choix, key="d_vitre")
    with t2:
        if type_fiche == "Appartement":
            st.text_input("Nom du Syndic / Contact", key="d_syndic")
        else:
            is_copro = st.radio("En copropriété / ASL ?", ["Non", "Oui"], horizontal=True)
            if is_copro == "Oui": st.text_input("Nom du Syndic", key="d_syndic_m")
        st.selectbox("Énergie Chauffage", ["Gaz", "Électricité", "PAC", "Fuel", "Bois"], key="d_chauff")
        st.selectbox("Eau Chaude", ["Cumulus Élec", "Chaudière Gaz", "Thermodynamique", "Solaire"], key="d_eau")

    st.markdown("---")
    st.subheader("📏 Tableau des Surfaces")
    for i in range(st.session_state.rows):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
        with sc2: st.number_input("m²", key=f"m{i}", step=0.01)
        with sc3: st.text_input("Notes", key=f"r{i}")
    st.button("➕ Ajouter une pièce", on_click=lambda: st.session_state.update({"rows": st.session_state.rows + 1}))

# --- SECTION 2 : EXTÉRIEURS & RISQUES ---
elif menu == "2. Extérieurs & Risques":
    e1, e2 = st.columns(2)
    with e1:
        st.subheader("🏡 Aménagements & Annexes")
        st.multiselect("Aménagements", ["Jardin", "Clôture", "Portail électrique", "Cuisine d'été"], placeholder=txt_choix, key="e_amen")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"], key="e_pisc")
        st.multiselect("Annexes", ["Garage", "Cave", "Abri de jardin", "Carport", "Terrasse"], placeholder=txt_choix, key="e_annex")
    with e2:
        st.subheader("🚫 Risques (ERP)")
        st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="e_sis")
        st.selectbox("Aléa Argiles (Retrait-gonflement)", ["Nul", "Faible", "Moyen", "Fort"], key="e_arg")
        st.checkbox("Zone Inondable", key="e_ino")
        st.checkbox("Risque Radon", key="e_rad")

# --- SECTION 3 : PATHOLOGIES (AJOUT DYNAMIQUE) ---
elif menu == "3. Diagnostic Pathologies":
    st.subheader("⚠️ Inventaire des désordres")
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢 Faible"})
    
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            c1, c2 = st.columns(2)
            p["loc"] = c1.text_input("Localisation", key=f"ploc_{idx}")
            p["type"] = c2.selectbox("Type", ["Fissure", "Humidité", "Infiltration", "Structure", "Autre"], key=f"ptyp_{idx}")
            p["grav"] = st.select_slider("Gravité", options=["🟢 Faible", "🟡 Moyenne", "🔴 Critique"], key=f"pgrav_{idx}")
            p["obs"] = st.text_area("Observations textuelles", key=f"pobs_{idx}")

# --- SECTION 4 : PHOTOS & SIGNATURE ---
elif menu == "4. Photos & Signature":
    st.subheader("📸 Reportage & Validation")
    up = st.file_uploader("Prendre/Ajouter des photos", accept_multiple_files=True, type=['jpg', 'png'])
    if up:
        for f in up:
            processed = process_image(f)
            st.image(processed, caption=f.name, width=200)
    st.markdown("---")
    st.text_input("Nom du signataire pour validation", key="s_nom")

# --- SECTION 5 : FACTURATION TTC ---
elif menu == "5. Facturation TTC":
    st.subheader("💰 Calculateur d'honoraires")
    f1, f2 = st.columns(2)
    with f1:
        hono_ttc = st.number_input("Honoraires Expertise TTC (€)", value=0.0)
        dist = st.number_input("Distance KM (Aller/Retour)", value=0)
    with f2:
        tarif_km = st.number_input("Tarif KM TTC (€/km)", value=0.60)
        tva = 20 # Pour le calcul HT
    
    ik_total = dist * tarif_km
    total_ttc = hono_ttc + ik_total
    total_ht = total_ttc / 1.2
    
    st.metric("TOTAL GÉNÉRAL TTC", f"{total_ttc:.2f} €")
    st.write(f"Dont Indemnités Kilométriques : {ik_total:.2f} €")
    st.info(f"Rappel Montant Hors Taxes (HT) : {total_ht:.2f} €")
    st.session_state["final_ttc"] = total_ttc

# --- BOUTON FINAL ---
st.markdown("---")
if st.button("📄 ÉDITER LE COMPTE-RENDU DE VISITE"):
    pdf = PDF()
    pdf.add_page()
    
    pdf.section_header(1, "DOSSIER TECHNIQUE")
    pdf.add_data("Client", st.session_state.get('d_client', ''))
    pdf.add_data("Adresse", st.session_state.get('d_adr', ''))
    pdf.add_data("Vitrages", ", ".join(st.session_state.get('d_vitre', [])))
    
    pdf.section_header(2, "RISQUES ET EXTERIEURS")
    pdf.add_data("Sismicite", st.session_state.get('e_sis', ''))
    pdf.add_data("Argiles", st.session_state.get('e_arg', ''))
    
    pdf.section_header(3, "PATHOLOGIES")
    for p in st.session_state.pathos:
        pdf.add_data(f"Désordre {p['type']} ({p['loc']})", f"Gravité {p['grav']}")

    pdf.section_header(4, "FINANCES")
    pdf.add_data("TOTAL TTC", f"{st.session_state.get('final_ttc', 0):.2f} Euros")

    res = pdf.output(dest='S').encode('latin-1', 'replace')
    st.download_button("📥 TÉLÉCHARGER LE PDF", res, "Expertise.pdf", "application/pdf")