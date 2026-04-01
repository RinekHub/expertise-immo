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
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.thumbnail((800, 800))
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=70)
        return img_byte_arr.getvalue()
    except:
        return None

# --- 2. LA CLASSE PDF (AVEC TOUTES LES FONCTIONS) ---
class PDF(FPDF):
    def header(self):
        # Gestion du Logo
        if os.path.exists("logo.png"):
            try:
                img = Image.open("logo.png")
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                img_temp = io.BytesIO()
                img.save(img_temp, format='JPEG')
                img_temp.seek(0)
                self.image(img_temp, 10, 8, 33)
            except:
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'FD EXPERTISE', 0, 1, 'L')
        else:
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'CABINET FD EXPERTISE', 0, 1, 'L')
            
        self.set_font('Arial', 'B', 14)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE', 0, 1, 'C')
        self.ln(5)

    # LA FONCTION QUI MANQUAIT :
    def section_header(self, num, label):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(230, 230, 230) # Grisage
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

# --- 4. INTERFACE ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    type_bien = st.radio("Type de Bien", ["Appartement", "Maison"])
    st.markdown("---")
    menu = st.radio("Navigation", ["1. Dossier Technique", "2. Extérieurs & Risques", "3. Diagnostic Pathologies", "4. Photos & Signature", "5. Facturation TTC"])

st.title(f"📋 Expertise {type_bien}")

# --- SECTIONS (Logique simplifiée pour test) ---
if menu == "1. Dossier Technique":
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Donneur d'ordre", key="d_client")
        adr = st.text_input("Adresse du bien", key="d_adr")
    with c2:
        st.text_input("Propriétaire", key="d_prop")
        st.text_input("Ville / CP", key="d_ville")
    st.multiselect("Vitrages", ["PVC Simple", "PVC Double", "Alu", "Bois"], key="d_vitre")

elif menu == "3. Diagnostic Pathologies":
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢 Faible"})
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            p["loc"] = st.text_input("Localisation", key=f"ploc_{idx}", value=p["loc"])
            p["type"] = st.selectbox("Type", ["Fissure", "Humidité", "Structure"], key=f"ptyp_{idx}")
            p["grav"] = st.select_slider("Gravité", options=["🟢 Faible", "🟡 Moyenne", "🔴 Critique"], key=f"pgrav_{idx}")

elif menu == "5. Facturation TTC":
    hono = st.number_input("Honoraires TTC (€)", value=0.0)
    st.session_state["final_ttc"] = hono
    st.metric("TOTAL TTC", f"{hono:.2f} €")

# --- 5. BOUTON GÉNÉRATION PDF ---
st.markdown("---")
if st.button("📄 ÉDITER LE COMPTE-RENDU DE VISITE"):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # Section 1
        pdf.section_header(1, "DOSSIER TECHNIQUE")
        pdf.add_data("Client", st.session_state.get('d_client'))
        pdf.add_data("Adresse", st.session_state.get('d_adr'))
        vitres = st.session_state.get('d_vitre', [])
        pdf.add_data("Vitrages", ", ".join(vitres) if vitres else "Non renseigné")
        
        # Section 2
        pdf.section_header(2, "PATHOLOGIES")
        if not st.session_state.pathos:
            pdf.add_data("Désordres", "Aucun signalé")
        for p in st.session_state.pathos:
            pdf.add_data(f"Désordre {p['type']}", f"{p['loc']} - {p['grav']}")
            
        # Section 3
        pdf.section_header(3, "FINANCES")
        pdf.add_data("TOTAL TTC", f"{st.session_state.get('final_ttc', 0):.2f} Euros")

        # Sortie
        res = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER LE PDF", res, "Expertise.pdf", "application/pdf")
        st.success("PDF Généré avec succès !")
        
    except Exception as e:
        st.error(f"Désolé, une erreur est survenue : {e}")