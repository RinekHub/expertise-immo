import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io
import urllib.parse

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

def process_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        if image.mode in ("RGBA", "P"): image = image.convert("RGB")
        image.thumbnail((800, 800))
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=70)
        return img_byte_arr.getvalue()
    except: return None

# --- 2. CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        # Logo simplifié (sécurité max)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'CABINET FD EXPERTISE', 0, 1, 'L')
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE', 0, 1, 'C')
        self.ln(5)

    def section_header(self, num, label):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(230, 230, 230)
        txt = f"{num}. {label}".encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 8, f" {txt}", 0, 1, 'L', 1)
        self.ln(2)

    def add_data(self, label, value):
        self.set_font('Arial', 'B', 9)
        lbl = f"{label} : ".encode('latin-1', 'replace').decode('latin-1')
        self.write(5, lbl)
        self.set_font('Arial', '', 9)
        val = str(value if value else "---").encode('latin-1', 'replace').decode('latin-1')
        self.write(5, f"{val}\n")

# --- 3. INITIALISATION ---
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 4

# --- 4. BARRE LATÉRALE ---
with st.sidebar:
    type_bien = st.radio("Type de Bien", ["Appartement", "Maison"])
    st.markdown("---")
    menu = st.radio("Navigation", [
        "1. Dossier Technique", 
        "2. Extérieurs & Risques", 
        "3. Diagnostic Pathologies", 
        "4. Photos & Signature",
        "5. Facturation TTC"
    ])

st.title(f"📋 Expertise {type_bien}")

# --- SECTION 1 : DOSSIER TECHNIQUE ---
if menu == "1. Dossier Technique":
    st.subheader("👤 Identification & Caractéristiques")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Donneur d'ordre", key="d_client")
        adresse = st.text_input("Adresse du bien", key="d_adr")
        if adresse:
            q = urllib.parse.quote(adresse)
            st.markdown(f"[📍 Voir sur Google Maps](https://www.google.com/maps/search/{q})")
    with c2:
        st.text_input("Propriétaire", key="d_prop")
        st.text_input("Ville / CP", key="d_ville")
    
    st.markdown("---")
    t1, t2 = st.columns(2)
    with t1:
        st.text_input("Année (Const./Rénov.)", key="d_annee")
        st.text_input("Étages / Niveaux", key="d_etage")
        st.multiselect("Menuiseries & Vitrage", ["PVC Double", "Alu Double", "Bois Simple", "Bois Double"], key="d_vitre")
    with t2:
        if type_bien == "Appartement": st.text_input("Syndic", key="d_syndic")
        else: st.text_input("Copro / ASL", key="d_copro")
        st.selectbox("Chauffage", ["Gaz", "Électricité", "PAC", "Bois"], key="d_chauff")
        st.selectbox("Eau Chaude", ["Cumulus", "Chaudière", "Thermodynamique"], key="d_eau")

# --- SECTION 2 : EXTÉRIEURS & RISQUES ---
elif menu == "2. Extérieurs & Risques":
    e1, e2 = st.columns(2)
    with e1:
        st.subheader("🏡 Aménagements & Annexes")
        st.multiselect("Aménagements", ["Jardin", "Clôture", "Portail électrique", "Cuisine d'été"], key="e_amen")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"], key="e_pisc")
        st.multiselect("Annexes", ["Garage", "Cave", "Abri jardin", "Carport", "Terrasse"], key="e_annex")
    with e2:
        st.subheader("🚫 ERP (Risques)")
        st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="e_sis")
        st.selectbox("Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="e_arg")
        st.checkbox("Inondations", key="e_ino")
        st.checkbox("Radon", key="e_rad")

# --- SECTION 3 : PATHOLOGIES ---
elif menu == "3. Diagnostic Pathologies":
    st.subheader("⚠️ Désordres détaillés")
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢 Faible", "obs": ""})
    
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            c1, c2 = st.columns(2)
            p["loc"] = st.text_input("Localisation", key=f"ploc_{idx}", value=p["loc"])
            p["type"] = st.selectbox("Type", ["Fissure", "Humidité", "Infiltration", "Structure"], key=f"ptyp_{idx}")
            p["grav"] = st.select_slider("Gravité", options=["🟢 Faible", "🟡 Moyenne", "🔴 Critique"], key=f"pgrav_{idx}")
            p["obs"] = st.text_area("Observations", key=f"pobs_{idx}", value=p["obs"])

# --- SECTION 4 : PHOTOS & SIGNATURE ---
elif menu == "4. Photos & Signature":
    st.subheader("📸 Validation")
    st.file_uploader("Upload compressé (Pillow)", accept_multiple_files=True, type=['jpg', 'png'])
    st.text_input("Nom du signataire", key="s_nom")

# --- SECTION 5 : FACTURATION TTC ---
elif menu == "5. Facturation TTC":
    st.subheader("💰 Calculateur d'honoraires")
    f1, f2 = st.columns(2)
    with f1:
        hono_ttc = st.number_input("Honoraires Expertise TTC (€)", value=0.0)
        dist = st.number_input("Distance KM (Aller/Retour)", value=0)
    with f2:
        tarif_km = st.number_input("Tarif KM TTC (€/km)", value=0.60)
    
    ik_total = dist * tarif_km
    total_general_ttc = hono_ttc + ik_total
    total_ht = total_general_ttc / 1.2
    
    st.markdown("---")
    st.metric("TOTAL GÉNÉRAL TTC", f"{total_general_ttc:.2f} €")
    st.write(f"Dont Indemnités Kilométriques : {ik_total:.2f} €")
    st.info(f"Rappel Montant Hors Taxes (HT) : {total_ht:.2f} €")
    st.session_state["final_ttc"] = total_general_ttc

# --- SECTION 6 : LE DOCUMENT FINAL ---
st.markdown("---")
if st.button("📄 ÉDITER LE COMPTE-RENDU DE VISITE"):
    try:
        pdf = PDF()
        pdf.add_page()
        
        pdf.section_header(1, "DOSSIER & TECHNIQUE")
        pdf.add_data("Client", st.session_state.get('d_client'))
        pdf.add_data("Adresse", st.session_state.get('d_adr'))
        pdf.add_data("Chauffage", st.session_state.get('d_chauff'))
        
        pdf.section_header(2, "EXTÉRIEURS & RISQUES")
        pdf.add_data("Sismique", st.session_state.get('e_sis'))
        pdf.add_data("Piscine", st.session_state.get('e_pisc'))
        
        pdf.section_header(3, "PATHOLOGIES")
        for p in st.session_state.pathos:
            pdf.add_data(f"Désordre {p['type']}", f"{p['loc']} - {p['grav']}")
            
        pdf.section_header(4, "FACTURATION")
        pdf.add_data("TOTAL TTC", f"{st.session_state.get('final_ttc', 0):.2f} Euros")

        res = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER LE RAPPORT", res, "Expertise.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erreur lors de l'édition : {e}")