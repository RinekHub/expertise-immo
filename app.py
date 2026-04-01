import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io
import urllib.parse

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- FONCTION DE RÉINITIALISATION (RGPD) ---
def reset_form():
    for key in st.keys():
        del st[key]
    st.rerun()

# --- 2. CLASSE PDF (AVEC LOGO) ---
class PDF(FPDF):
    def header(self):
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
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

# --- 3. INITIALISATION ---
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 5

# --- 4. BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=150)
    
    st.markdown("---")
    type_bien = st.radio("🏠 Type de Bien", ["Appartement", "Maison"])
    
    st.markdown("---")
    menu = st.radio("📍 Navigation", [
        "1. Identification & Immeuble", 
        "2. Surfaces & Annexes", 
        "3. Extérieurs & Risques", 
        "4. Pathologies", 
        "5. Honoraires"
    ])

    st.markdown("---")
    # LE BOUTON DE NETTOYAGE RGPD
    if st.button("🗑️ EFFACER TOUT LE FORMULAIRE", help="Supprime toutes les données saisies"):
        st.session_state.clear()
        st.rerun()

st.title(f"📋 Expertise : {type_bien}")

# --- SECTION 1 : IDENTIFICATION ---
if menu == "1. Identification & Immeuble":
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👤 Client")
        st.text_input("Donneur d'ordre", key="d_client")
        st.text_input("Adresse", key="d_adr")
    with c2:
        st.subheader("🏢 Immeuble")
        st.text_input("Année", key="i_annee")
        st.selectbox("Situation locative", ["Libre", "Occupé", "Loué"], key="i_loc")
        if type_bien == "Appartement":
            st.text_input("Étage", key="i_etage")
            st.text_input("Syndic", key="i_syndic")
        else:
            st.selectbox("Assainissement", ["Tout à l'égout", "Fosse Septique"], key="i_assain")
            st.text_input("Terrain (m²)", key="i_terrain")
    
    st.multiselect("Menuiseries", ["Bois", "PVC", "Alu", "Double Vitrage"], key="i_menuis")

# --- SECTION 2 : SURFACES ---
elif menu == "2. Surfaces & Annexes":
    st.subheader("📏 Surfaces")
    for i in range(st.session_state.rows):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
        with sc2: st.number_input("m²", key=f"m{i}", step=0.01)
        with sc3: st.text_input("Notes", key=f"r{i}")
    st.button("➕ Ligne", on_click=lambda: st.session_state.update({"rows": st.session_state.rows + 1}))

    st.markdown("---")
    st.subheader("📦 Annexes")
    st.multiselect("Annexes", ["Cave", "Parking", "Garage", "Terrasse", "Grenier"], key="a_liste")
    st.text_area("Observations annexes", key="a_obs")

# --- SECTION 3 : EXTÉRIEURS ---
elif menu == "3. Extérieurs & Risques":
    if type_bien == "Maison":
        st.multiselect("Aménagements", ["Jardin", "Piscine", "Portail élec"], key="e_amen")
    st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="e_sis")
    st.checkbox("Zone Inondable", key="e_inond")

# --- SECTION 4 : PATHOLOGIES ---
elif menu == "4. Pathologies":
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢 Faible", "obs": ""})
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            p["loc"] = st.text_input("Lieu", key=f"ploc_{idx}", value=p.get("loc", ""))
            p["type"] = st.selectbox("Type", ["Fissure", "Humidité", "Structure"], key=f"ptyp_{idx}")
            p["grav"] = st.select_slider("Gravité", options=["🟢", "🟡", "🔴"], key=f"pgrav_{idx}")
            p["obs"] = st.text_area("Observations", key=f"pobs_{idx}", value=p.get("obs", ""))

# --- SECTION 5 : HONORAIRES ---
elif menu == "5. Honoraires":
    h_ttc = st.number_input("Hono TTC (€)", value=0.0, key="h_val")
    dist = st.number_input("Distance KM (A/R)", value=0, key="dist_val")
    t_km = st.number_input("Tarif KM", value=0.60, key="tk_val")
    total = h_ttc + (dist * t_km)
    st.metric("TOTAL TTC", f"{total:.2f} €")
    st.session_state["final_ttc"] = total

# --- GÉNÉRATION PDF ---
st.markdown("---")
if st.button("📄 GÉNÉRER LE RAPPORT PDF"):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.section_header(f"IDENTIFICATION DU BIEN ({type_bien})")
        pdf.add_data("Client", st.session_state.get('d_client'))
        pdf.add_data("Adresse", st.session_state.get('d_adr'))
        
        pdf.section_header("SURFACES")
        for i in range(st.session_state.rows):
            p_n = st.session_state.get(f"p{i}")
            if p_n: pdf.add_data(p_n, f"{st.session_state.get(f'm{i}')} m2")

        pdf.section_header("FINANCES")
        pdf.add_data("TOTAL TTC", f"{st.session_state.get('final_ttc', 0):.2f} Euros")

        res = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER", res, "Expertise.pdf", "application/pdf")
    except Exception as e: st.error(f"Erreur : {e}")