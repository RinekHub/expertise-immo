import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- CLASSE PDF DÉTAILLÉE ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 33)
        self.set_font('Arial', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE', 0, 0, 'C')
        self.ln(20)

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, f"  {label}".encode('latin-1', 'replace').decode('latin-1'), 0, 1, 'L', 1)
        self.ln(2)

    def data_line(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.write(5, f"{label} : ".encode('latin-1', 'replace').decode('latin-1'))
        self.set_font('Arial', '', 10)
        self.write(5, f"{value}\n".encode('latin-1', 'replace').decode('latin-1'))

# --- INITIALISATION ---
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'pieces' not in st.session_state: st.session_state.pieces = [{"nom": "", "surface": 0.0}]

# --- BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", use_container_width=True)
    type_bien = st.radio("Nature du bien", ["Appartement", "Maison"])
    menu = st.radio("Navigation", ["Identification", "Technique", "Extérieurs & Risques", "Pathologies", "Surfaces", "Facturation TTC"])

# --- 1. IDENTIFICATION ---
if menu == "Identification":
    st.subheader("👤 Identification du Dossier")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Donneur d'ordre", key="donneur")
        st.text_input("Propriétaire", key="proprio")
        addr = st.text_input("Adresse précise du bien", key="adresse")
        if addr: st.markdown(f"📍 [Localiser sur Maps](http://maps.google.com/?q={addr.replace(' ', '+')})")
    with col2:
        st.text_input("Année de construction / Facteur année", key="annee")
        st.text_input("Nombre de niveaux", key="niveaux")
        if type_bien == "Appartement":
            st.text_input("Syndic (Nom et Contact)", key="syndic")
        else:
            st.checkbox("Bien en copropriété horizontale", key="copro_h")

# --- 2. TECHNIQUE ---
elif menu == "Technique":
    st.subheader("🛠️ Caractéristiques Techniques")
    t1, t2 = st.columns(2)
    with t1:
        st.multiselect("Matériaux menuiseries", ["PVC", "Aluminium", "Bois", "Mixte"], key="menuis_mat")
        st.selectbox("Type de vitrage", ["Simple", "Double vitrage", "Double phonique", "Triple vitrage"], key="vitrage")
        st.selectbox("État des menuiseries", ["Parfait", "Bon état", "Usager", "Vétuste"], key="menuis_etat")
    with t2:
        st.selectbox("Énergie Chauffage", ["Gaz", "Électricité", "Fuel", "PAC Air/Eau", "PAC Air/Air", "Bois/Granulés"], key="chauff_en")
        st.selectbox("Production Eau Chaude", ["Cumulus Élec", "Chaudière", "Solaire", "Thermodynamique"], key="ecs")
        st.selectbox("Situation locative", ["Libre", "Bail en cours", "Meublé", "Saisonnier"], key="sit_loc")

# --- 3. EXTÉRIEURS & RISQUES ---
elif menu == "Extérieurs & Risques":
    st.subheader("🏡 Aménagements Extérieurs")
    e1, e2 = st.columns(2)
    with e1:
        st.multiselect("Équipements", ["Clôture", "Portail motorisé", "Arrosage automatique", "Puits/Forage", "Cuisine d'été", "Éclairage jardin"], key="ext_equip")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol", "Bassin"], key="piscine_type")
        st.multiselect("Sécurité/Option Piscine", ["Alarme", "Volet roulant", "Chauffage", "Traitement Sel"], key="piscine_options")
    with e2:
        st.multiselect("Annexes présentes", ["Garage", "Cave", "Carport", "Abri jardin", "Grenier", "Terrasse", "Balcon"], key="annexes")
    
    st.markdown("---")
    st.subheader("🚫 État des Risques (ERP)")
    r1, r2 = st.columns(2)
    with r1:
        st.selectbox("Zone Sismique", ["1 (Très faible)", "2", "3", "4", "5 (Fort)"], key="erp_seisme")
        st.selectbox("Retrait-Gonflement Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="erp_argile")
    with r2:
        st.checkbox("Zone Inondable", key="erp_inond")
        st.checkbox("Risque Radon", key="erp_radon")

# --- 4. PATHOLOGIES ---
elif menu == "Pathologies":
    st.subheader("⚠️ Désordres & Pathologies")
    if st.button("➕ Ajouter une pathologie"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "Faible", "obs": ""})
    
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            st.session_state.pathos[idx]["loc"] = st.text_input("Localisation précise", value=p["loc"], key=f"ploc_{idx}")
            st.session_state.pathos[idx]["type"] = st.selectbox("Nature", ["Fissure structurelle", "Fissure de retrait", "Humidité", "Infiltration", "Remontée capillaire", "Termites/Parasites"], key=f"ptyp_{idx}")
            st.session_state.pathos[idx]["grav"] = st.select_slider("Niveau de gravité", options=["Faible", "Moyen", "Critique"], key=f"pgrav_{idx}")
            st.session_state.pathos[idx]["obs"] = st.text_area("Préconisations", value=p["obs"], key=f"pobs_{idx}")

# --- 5. SURFACES ---
elif menu == "Surfaces":
    st.subheader("📏 Relevé des surfaces par pièce")
    if st.button("➕ Ajouter une pièce"):
        st.session_state.pieces.append({"nom": "", "surface": 0.0})
    for i, piece in enumerate(st.session_state.pieces):
        c1, c2 = st.columns([3, 1])
        st.session_state.pieces[i]["nom"] = c1.text_input(f"Nom de la pièce {i+1}", value=piece["nom"], key=f"pnom_{i}")
        st.session_state.pieces[i]["surface"] = c2.number_input("m²", value=piece["surface"], key=f"psurf_{i}")

# --- 6. FACTURATION TTC ---
elif menu == "Facturation TTC":
    st.subheader("💰 Synthèse Financière")
    hono = st.number_input("Honoraires d'expertise TTC (€)", value=0.0, key="f_hono")
    km = st.number_input("Nombre de kilomètres (A/R)", value=0, key="f_km")
    t_km = st.number_input("Tarif kilométrique TTC (€/km)", value=0.60)
    total = hono + (km * t_km)
    st.metric("TOTAL GÉNÉRAL TTC", f"{total:.2f} €")
    st.session_state["total_f"] = total

# --- BOUTON FINAL ---
st.markdown("---")
if st.button("📄 ÉDITER LE COMPTE-RENDU DE VISITE"):
    pdf = PDF()
    pdf.add_page()
    
    # 1. Identification
    pdf.section_title("1. IDENTIFICATION")
    pdf.data_line("Donneur d'ordre", st.session_state.get('donneur', ''))
    pdf.data_line("Adresse", st.session_state.get('adresse', ''))
    pdf.data_line("Année", st.session_state.get('annee', ''))
    
    # 2. Technique
    pdf.section_title("2. TECHNIQUE ET ENERGIE")
    pdf.data_line("Matériaux", ", ".join(st.session_state.get('menuis_mat', [])))
    pdf.data_line("Vitrage", st.session_state.get('vitrage', ''))
    pdf.data_line("Chauffage", st.session_state.get('chauff_en', ''))
    pdf.data_line("Eau chaude", st.session_state.get('ecs', ''))

    # 3. Extérieurs
    pdf.section_title("3. AMENAGEMENTS EXTERIEURS ET RISQUES")
    pdf.data_line("Equipements", ", ".join(st.session_state.get('ext_equip', [])))
    pdf.data_line("Piscine", st.session_state.get('piscine_type', ''))
    pdf.data_line("Annexes", ", ".join(st.session_state.get('annexes', [])))
    pdf.data_line("Zone Sismique", st.session_state.get('erp_seisme', ''))
    pdf.data_line("Argiles", st.session_state.get('erp_argile', ''))

    # 4. Pathologies
    pdf.section_title("4. PATHOLOGIES CONSTATEES")
    if not st.session_state.pathos:
        pdf.write(5, "Néant.\n")
    for p in st.session_state.pathos:
        pdf.set_font('Arial', 'B', 10)
        pdf.write(5, f"- {p['type']} ({p['loc']}) : ")
        pdf.set_font('Arial', '', 10)
        pdf.write(5, f"Gravité {p['grav']}. Obs: {p['obs']}\n")
    pdf.ln(5)

    # 5. Surfaces
    pdf.section_title("5. TABLEAU DES SURFACES")
    for p in st.session_state.pieces:
        if p["nom"]: pdf.data_line(p["nom"], f"{p['surface']} m2")

    # 6. Finance
    pdf.section_title("6. SYNTHESE FINANCIERE")
    pdf.data_line("TOTAL DE LA PRESTATION", f"{st.session_state.get('total_f', 0):.2f} Euros TTC")

    # Téléchargement
    res = pdf.output(dest='S').encode('latin-1', 'replace')
    st.download_button("📥 TÉLÉCHARGER LE COMPTE-RENDU (PDF)", res, f"Compte_Rendu_{st.session_state.get('donneur')}.pdf", "application/pdf")