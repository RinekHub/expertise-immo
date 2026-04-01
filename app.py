import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

def process_image(uploaded_file):
    image = Image.open(uploaded_file)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.thumbnail((800, 800))
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG', quality=70)
    return img_byte_arr.getvalue()

# --- CLASSE PDF AMÉLIORÉE ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            try:
                img = Image.open("logo.png")
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                img_temp = io.BytesIO()
                img.save(img_temp, format='JPEG')
                img_temp.seek(0)
                self.image(img_temp, 10, 8, 33, type='JPEG')
            except:
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'FD EXPERTISE', 0, 0, 'L')
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE', 0, 1, 'C')
        self.ln(10)

    def section_header(self, num, label):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(230, 230, 230)
        # Nettoyage strict pour éviter l'AttributeError sur les accents
        clean_label = str(label).encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 8, f" {num}. {clean_label}", 0, 1, 'L', 1)
        self.ln(2)

    def add_data(self, label, value):
        self.set_font('Arial', 'B', 9)
        lbl = f"{str(label)} : ".encode('latin-1', 'replace').decode('latin-1')
        self.write(5, lbl)
        self.set_font('Arial', '', 9)
        # Si la valeur est vide, on met "---"
        val_str = str(value) if value else "---"
        val = val_str.encode('latin-1', 'replace').decode('latin-1')
        self.write(5, f"{val}\n")

# --- INITIALISATION ---
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 4

# --- BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width='stretch')
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
    st.subheader("👤 Identification")
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
    st.subheader("🏠 Technique")
    t1, t2 = st.columns(2)
    with t1:
        st.text_input("Année (Const./Rénov.)", key="d_annee")
        st.multiselect("Vitrages & Matériaux", ["PVC Simple vitrage", "PVC Double vitrage", "Alu", "Bois"], key="d_vitre")
    with t2:
        st.selectbox("Chauffage", ["Gaz", "Électricité", "PAC", "Bois"], key="d_chauff")
        st.selectbox("Eau Chaude", ["Cumulus Élec", "Gaz", "Thermodynamique"], key="d_eau")

    st.markdown("---")
    st.subheader("📏 Surfaces")
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
        st.subheader("🏡 Aménagements")
        st.multiselect("Équipements", ["Jardin", "Portail élec", "Cuisine d'été"], key="e_amen")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"], key="e_pisc")
    with e2:
        st.subheader("🚫 Risques (ERP)")
        st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="e_sis")
        st.selectbox("Aléa Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="e_arg")

# --- SECTION 3 : PATHOLOGIES ---
elif menu == "3. Diagnostic Pathologies":
    st.subheader("⚠️ Désordres")
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢 Faible", "obs": ""})
    
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            c1, c2 = st.columns(2)
            p["loc"] = st.text_input("Localisation", key=f"ploc_{idx}", value=p.get("loc", ""))
            p["type"] = st.selectbox("Type", ["Fissure", "Humidité", "Structure"], key=f"ptyp_{idx}")
            p["grav"] = st.select_slider("Gravité", options=["🟢 Faible", "🟡 Moyenne", "🔴 Critique"], key=f"pgrav_{idx}")
            p["obs"] = st.text_area("Observations", key=f"pobs_{idx}", value=p.get("obs", ""))

# --- SECTION 4 : PHOTOS & SIGNATURE ---
elif menu == "4. Photos & Signature":
    st.subheader("📸 Validation")
    st.file_uploader("Prendre/Ajouter des photos", accept_multiple_files=True, type=['jpg', 'png'])
    st.text_input("Nom du signataire", key="s_nom")

# --- SECTION 5 : FACTURATION ---
elif menu == "5. Facturation TTC":
    f1, f2 = st.columns(2)
    with f1:
        hono = st.number_input("Honoraires TTC (€)", value=0.0)
        dist = st.number_input("Distance KM", value=0)
    with f2:
        tarif_km = st.number_input("Tarif KM TTC", value=0.60)
    total = hono + (dist * tarif_km)
    st.metric("TOTAL TTC", f"{total:.2f} €")
    st.session_state["final_ttc"] = total

# --- BOUTON GÉNÉRATION ---
st.markdown("---")
if st.button("📄 ÉDITER LE COMPTE-RENDU DE VISITE"):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # 1. Dossier Technique
        pdf.section_header(1, "DOSSIER TECHNIQUE")
        pdf.add_data("Client", st.session_state.get('d_client', '---'))
        pdf.add_data("Adresse", st.session_state.get('d_adr', '---'))
        vitres = st.session_state.get('d_vitre', [])
        pdf.add_data("Vitrages", ", ".join(vitres) if vitres else "Non renseigné")
        
        # 2. Pathologies
        pdf.section_header(2, "PATHOLOGIES")
        if not st.session_state.pathos:
            pdf.add_data("Désordres", "Aucun désordre signalé.")
        else:
            for p in st.session_state.pathos:
                loc = p.get('loc', 'Lieu inconnu')
                typ = p.get('type', 'Type inconnu')
                pdf.add_data(f"Désordre {typ}", f"{loc} - Gravité {p.get('grav')}")
        
        # 3. Finances
        pdf.section_header(3, "FINANCES")
        pdf.add_data("TOTAL TTC", f"{st.session_state.get('final_ttc', 0):.2f} Euros")

        # Sortie du PDF
        res = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER LE PDF", res, "Expertise.pdf", "application/pdf")
        st.success("PDF prêt !")
        
    except Exception as e:
        st.error(f"Désolé, une erreur est survenue : {e}")