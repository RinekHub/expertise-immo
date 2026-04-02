import streamlit as st
import os
import json
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURATION & DOSSIER SERVEUR ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")
SAVE_DIR = "sauvegardes"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- 2. LOGIQUE DE SAUVEGARDE (ANTI-PERTE) ---
def sauver_sur_serveur():
    """Enregistre tout le contenu du formulaire dans un fichier sur le serveur"""
    # On capture tout ce qui est dans la session (les inputs avec des 'key')
    data = {k: v for k, v in st.session_state.items() if not k.startswith('FormSubmitter')}
    with open(os.path.join(SAVE_DIR, "sauvegarde_en_cours.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def charger_depuis_serveur():
    """Récupère les données au démarrage de l'app"""
    path = os.path.join(SAVE_DIR, "sauvegarde_en_cours.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                st.session_state[k] = v

# --- 3. INITIALISATION ---
if 'init_done' not in st.session_state:
    charger_depuis_serveur()
    st.session_state['init_done'] = True

if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 5

# --- 4. CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            try:
                img = Image.open("logo.png")
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                img_temp = io.BytesIO()
                img.save(img_temp, format='JPEG')
                img_temp.seek(0)
                self.image(img_temp, 10, 8, 33)
                self.ln(12)
            except: pass
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE', 0, 1, 'C')
        self.ln(5)

    def section_header(self, label):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(230, 230, 230)
        txt = label.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 8, f" {txt}", 0, 1, 'L', 1)
        self.ln(2)

    def add_data(self, label, value):
        self.set_font('Arial', 'B', 9)
        lbl = f"{label} : ".encode('latin-1', 'replace').decode('latin-1')
        self.write(5, lbl)
        self.set_font('Arial', '', 9)
        val = str(value if value else "---").encode('latin-1', 'replace').decode('latin-1')
        self.write(5, f"{val}\n")

# --- 5. BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=150)
    st.markdown("---")
    # Choix du bien avec sauvegarde immédiate
    type_bien = st.radio("🏠 Type de Bien", ["Appartement", "Maison"], key="type_bien", on_change=sauver_sur_serveur)
    st.markdown("---")
    menu = st.radio("📍 Navigation", ["📝 1. Expertise Technique", "💰 2. Facturation & PDF"])
    st.markdown("---")
    
    # BOUTON RGPD : Efface la session ET le fichier serveur
    if st.button("🗑️