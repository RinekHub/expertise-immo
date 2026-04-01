import streamlit as st
import os
import json
from fpdf import FPDF
from PIL import Image
import io
import urllib.parse

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- FONCTIONS DE SAUVEGARDE ---
def save_data(name):
    data = {key: st.session_state[key] for key in st.session_state.keys()}
    if not os.path.exists("sauvegardes"): os.makedirs("sauvegardes")
    with open(f"sauvegardes/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    st.success(f"✅ Dossier '{name}' sauvegardé !")

def load_data(name):
    with open(f"sauvegardes/{name}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        for key, value in data.items(): st.session_state[key] = value
    st.info(f"📂 Dossier '{name}' chargé !")

# --- 2. CLASSE PDF ---
class PDF(FPDF):
    def header(self):
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
    st.header("💾 Dossiers")
    nom_dos = st.text_input("Nom du dossier", value="Expertise_01")
    c_s1, c_s2 = st.columns(2)
    with c_s1: 
        if st.button("Sauver"): save_data(nom_dos)
    with c_s2:
        if os.path.exists("sauvegardes"):
            fichiers = [f.replace(".json", "") for f in os.listdir("sauvegardes") if f.endswith(".json")]
            if fichiers:
                sel = st.selectbox("Charger", fichiers)
                if st.button("Ouvrir"): load_data(sel)

    st.markdown("---")
    type_bien = st.radio("Type de Bien", ["Appartement", "Maison"])
    menu = st.radio("Navigation", ["1. Dossier Technique", "2. Extérieurs & Risques", "3. Diagnostic Pathologies", "4. Facturation TTC"])

st.title(f"📋 Expertise {type_bien}")

# --- SECTION 1 : DOSSIER TECHNIQUE & SURFACES ---
if menu == "1. Dossier Technique":
    st.subheader("👤 Identification")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Donneur d'ordre", key="d_client")
        adresse = st.text_input("Adresse du bien", key="d_adr")
    with c2:
        st.text_input("Propriétaire", key="d_prop")
        st.text_input("Ville / CP", key="d_ville")
    
    st.markdown("---")
    st.subheader("🏠 Technique")
    t1, t2 = st.columns(2)
    with t1:
        st.text_input("Année (Const./Rénov.)", key="d_annee")
        st.multiselect("Vitrages", ["PVC Double", "Alu Double", "Bois Simple", "Bois Double"], key="d_vitre", placeholder="Choisir...")
    with t2:
        if type_bien == "Appartement": st.text_input("Syndic", key="d_syndic")
        else: st.text_input("Copro / ASL", key="d_copro")
        st.selectbox("Chauffage", ["Gaz", "Électricité", "PAC", "Bois"], key="d_chauff")

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
        st.subheader("🏡 Aménagements")
        st.multiselect("Équipements", ["Jardin", "Portail élec", "Cuisine d'été"], key="e_amen", placeholder="Choisir...")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"], key="e_pisc")
        st.multiselect("Annexes", ["Garage", "Cave", "Abri jardin", "Terrasse"], key="e_annex", placeholder="Choisir...")
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
            p["loc"] = st.text_input("Localisation", key=f"ploc_{idx}", value=p.get("loc", ""))
            p["type"] = st.selectbox("Type", ["Fissure", "Humidité", "Structure"], key=f"ptyp_{idx}")
            p["grav"] = st.select_slider("Gravité", options=["🟢 Faible", "🟡 Moyenne", "🔴 Critique"], key=f"pgrav_{idx}")
            p["obs"] = st.text_area("Observations", key=f"pobs_{idx}", value=p.get("obs", ""))

# --- SECTION 4 : FACTURATION TTC ---
elif menu == "4. Facturation TTC":
    st.subheader("💰 Calculateur")
    f1, f2 = st.columns(2)
    with f1:
        h_ttc = st.number_input("Honoraires TTC (€)", value=0.0, key="h_val")
        dist = st.number_input("Distance KM (A/R)", value=0, key="dist_val")
    with f2:
        t_km = st.number_input("Tarif KM TTC (€/km)", value=0.60, key="tk_val")
    
    total_ttc = h_ttc + (dist * t_km)
    st.metric("TOTAL GÉNÉRAL TTC", f"{total_ttc:.2f} €")
    st.info(f"Rappel HT (TVA 20%) : {total_ttc/1.2:.2f} €")
    st.session_state["final_ttc"] = total_ttc

# --- BOUTON GÉNÉRATION ---
st.markdown("---")
if st.button("📄 ÉDITER LE PDF"):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.section_header(1, "DOSSIER TECHNIQUE")
        pdf.add_data("Client", st.session_state.get('d_client'))
        pdf.add_data("Adresse", st.session_state.get('d_adr'))
        
        pdf.section_header(2, "SURFACES")
        for i in range(st.session_state.rows):
            p_n = st.session_state.get(f"p{i}")
            if p_n: pdf.add_data(p_n, f"{st.session_state.get(f'm{i}')} m2")

        pdf.section_header(3, "PATHOLOGIES")
        for p in st.session_state.pathos:
            pdf.add_data(f"Désordre {p['type']}", f"{p['loc']} - {p['grav']}")

        pdf.section_header(4, "FACTURATION")
        pdf.add_data("TOTAL TTC", f"{st.session_state.get('final_ttc', 0):.2f} Euros")

        res = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER LE RAPPORT", res, "Expertise.pdf", "application/pdf")
    except Exception as e: st.error(f"Erreur : {e}")