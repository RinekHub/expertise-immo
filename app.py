import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 5

# --- 2. CLASSE PDF (RETOUR AU SOCLE INITIAL) ---
class PDF(FPDF):
    def header(self):
        # Affichage du logo sans fioritures comme au début
        if os.path.exists("logo.png"):
            try:
                # Correction technique invisible pour l'iPad mais garde l'aspect d'origine
                img = Image.open("logo.png")
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                img_temp = io.BytesIO()
                img.save(img_temp, format='JPEG')
                img_temp.seek(0)
                self.image(img_temp, 10, 8, 33)
                self.ln(12)
            except:
                pass
        
        # POLICE D'ORIGINE (Helvetica/Arial Standard)
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE', 0, 1, 'C')
        self.ln(5)

    def section_header(self, label):
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(230, 230, 230)
        # Gestion des accents d'origine
        txt = label.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 8, f" {txt}", 0, 1, 'L', 1)
        self.ln(2)

    def add_data(self, label, value):
        self.set_font('Helvetica', 'B', 9)
        lbl = f"{label} : ".encode('latin-1', 'replace').decode('latin-1')
        self.write(5, lbl)
        self.set_font('Helvetica', '', 9)
        val = str(value if value else "---").encode('latin-1', 'replace').decode('latin-1')
        self.write(5, f"{val}\n")

# --- 3. BARRE LATÉRALE (LOGO EN PREMIER) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    st.markdown("---")
    type_bien = st.radio("🏠 Type de Bien", ["Appartement", "Maison"], key="type_bien")
    st.markdown("---")
    if st.button("🗑️ NOUVEAU DOSSIER (RESET)"):
        st.session_state.clear()
        st.rerun()

st.title(f"Cabinet FD Expertise : {type_bien}")

# --- SECTION 1 : IDENTIFICATION ---
st.header("1. Section Dossier & Technique")
c1, c2 = st.columns(2)
with c1:
    st.text_input("Donneur d'ordre", key="d_client")
    st.text_input("Propriétaire", key="d_prop")
    st.text_input("Adresse du bien", key="d_adr")
with c2:
    st.text_input("Facteur Année", key="i_annee")
    st.selectbox("Situation Locative", ["Libre", "Occupé", "Loué", "Vides"], key="i_loc")
    if type_bien == "Appartement":
        st.text_input("Syndic", key="i_syndic")
        st.checkbox("Ascenseur", key="i_asc")
    else:
        st.checkbox("Maison en Copropriété", key="i_copro_m")

st.markdown("---")

# --- SECTION 2 : ÉNERGIES & MENUISERIES ---
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

# --- SECTION 3 : EXTÉRIEURS & RISQUES ---
st.header("3. Extérieurs & Risques")
e1, e2 = st.columns(2)
with e1:
    if type_bien == "Maison":
        st.text_input("Terrain (Clôture, Puits, etc.)", key="t_terrain")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"], key="t_piscine")
    st.selectbox("Entretien Général", ["Excellent", "Bon", "Moyen", "Négligé"], key="i_entretien")
with e2:
    st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="erp_sis")
    st.selectbox("Aléa Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="erp_arg")

st.markdown("---")

# --- SECTION 4 : PATHOLOGIES ---
st.header("4. Pathologies")
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

# --- SECTION 5 : SURFACES (POSITION BASSE) ---
st.header("5. Tableau des Surfaces")
for i in range(st.session_state.rows):
    sc1, sc2, sc3 = st.columns([2, 1, 2])
    with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
    with sc2: st.number_input("m²", key=f"m{i}", step=0.01)
    with sc3: st.text_input("État/Obs", key=f"r{i}")
if st.button("➕ Ajouter une ligne"):
    st.session_state.rows += 1
    st.rerun()

st.markdown("---")

# --- SECTION 6 : FACTURATION & SIGNATURE ---
st.header("6. Facturation & Signature")
f1, f2, f3 = st.columns(3)
with f1: h_ttc = st.number_input("Hono TTC (€)", key="h_val")
with f2: dist = st.number_input("Distance KM (A/R)", key="dist_val")
with f3: t_km = st.number_input("Tarif KM", value=0.60, key="tk_val")

total = h_ttc + (dist * t_km)
st.metric("TOTAL GÉNÉRAL TTC", f"{total:.2f} €")
st.text_input("🖋️ Signature (Nom du signataire)", key="signature_nom")

st.markdown("---")

# --- SECTION 7 : DOCUMENTS (POSITION FINALE) ---
st.header("7. Photos & Documents")
st.file_uploader("📸 Ajouter des photos", accept_multiple_files=True, key="photos_fin")

# --- BOUTON PDF ---
st.markdown("---")
if st.button("📄 GÉNÉRER LE RAPPORT FINAL"):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.section_header("Identification")
        pdf.add_data("Client", st.session_state.d_client)
        pdf.add_data("Adresse", st.session_state.d_adr)
        
        pdf.section_header("Surfaces")
        for i in range(st.session_state.rows):
            if st.session_state.get(f"p{i}"):
                pdf.add_data(st.session_state[f"p{i}"], f"{st.session_state[f'm{i}']} m2")

        pdf.section_header("Synthèse Financière")
        pdf.add_data("Total TTC", f"{total:.2f} Euros")

        buf = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER LE PDF", buf, "Rapport_Expertise_FD.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erreur : {e}")