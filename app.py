import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- CLASSE PDF SÉCURISÉE ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 33)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE', 0, 1, 'C')
        self.ln(10)

    def section_header(self, label):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(220, 220, 220)
        # Sécurité pour les accents dans les titres
        txt = label.encode('latin-1', 'replace').decode('latin-1')
        self.cell(0, 8, f" {txt}", 0, 1, 'L', 1)
        self.ln(2)

    def add_data(self, label, value):
        self.set_font('Arial', 'B', 9)
        lbl = f"{label} : ".encode('latin-1', 'replace').decode('latin-1')
        self.write(5, lbl)
        self.set_font('Arial', '', 9)
        val = str(value).encode('latin-1', 'replace').decode('latin-1')
        self.write(5, f"{val}\n")

# --- INITIALISATION DES VARIABLES ---
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'pieces' not in st.session_state: st.session_state.pieces = [{"nom": "", "surface": 0.0, "note": ""}]

# --- BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"): 
        st.image("logo.png", use_container_width=True)
    st.title("Menu Expertise")
    menu = st.radio("Navigation", [
        "1. Dossier & Technique (Fusion)", 
        "2. Extérieurs & Risques ERP", 
        "3. Diagnostic Pathologies", 
        "4. Tableau des Surfaces",
        "5. Photos & Signature",
        "6. Facturation TTC"
    ])
    st.markdown("---")
    type_bien = st.radio("Nature du bien :", ["Maison Individuelle", "Appartement"])

st.title(f"📑 {menu}")

# La consigne pour les menus déroulants
txt_choix = "Choisissez une ou plusieurs options"

# --- 1. DOSSIER & TECHNIQUE ---
if menu == "1. Dossier & Technique (Fusion)":
    st.subheader("👤 Identification & 🛠️ Technique")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Donneur d'ordre / Client", key="f_donneur")
        st.text_input("Propriétaire", key="f_proprio")
        st.text_input("Adresse complète", key="f_addr")
        st.text_input("Ville / CP", key="f_ville")
    with c2:
        st.text_input("Année de construction", key="f_annee")
        st.text_input("Nombre de niveaux", key="f_niveaux")
        if type_bien == "Appartement":
            st.text_input("Nom du Syndic", key="f_syndic")
        else:
            st.radio("En lotissement / ASL ?", ["Non", "Oui"], key="f_asl")

    st.markdown("---")
    t1, t2 = st.columns(2)
    with t1:
        # Lignes PVC demandées incluses ici
        st.multiselect("Matériaux et Vitrages", [
            "PVC Simple vitrage", 
            "PVC Double vitrage", 
            "Aluminium Simple vitrage",
            "Aluminium Double vitrage",
            "Bois Simple vitrage",
            "Bois Double vitrage",
            "Double vitrage phonique",
            "Triple vitrage",
            "Mixte Bois/Alu",
            "Acier"
        ], placeholder=txt_choix, key="f_mat_vitre")
        st.selectbox("État des menuiseries", ["Excellent", "Bon état", "Moyen", "Vétuste"], key="f_etat_m")
    with t2:
        st.selectbox("Énergie Chauffage", ["Gaz", "Électricité", "Fuel", "PAC", "Bois", "Géothermie"], key="f_chauff")
        st.multiselect("Distribution", ["Radiateurs", "Plancher chauffant", "Clim réversible", "Poêle"], placeholder=txt_choix, key="f_distri")
        st.selectbox("Production Eau Chaude", ["Cumulus Élec", "Chaudière", "Solaire", "Thermodynamique"], key="f_ecs")

# --- 2. EXTÉRIEURS & RISQUES ---
elif menu == "2. Extérieurs & Risques ERP":
    e1, e2 = st.columns(2)
    with e1:
        st.subheader("🏡 Aménagements")
        st.multiselect("Éléments Terrain", ["Clôture", "Portail motorisé", "Arrosage", "Puits", "Cuisine d'été"], placeholder=txt_choix, key="f_ext_e")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"], key="f_pisc")
    with e2:
        st.subheader("📦 Annexes")
        st.multiselect("Dépendances", ["Garage", "Cave", "Carport", "Abri jardin", "Terrasse", "Balcon"], placeholder=txt_choix, key="f_annexes")

    st.markdown("---")
    st.subheader("🚫 État des Risques (ERP)")
    st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="f_erp_s")
    st.selectbox("Aléa Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="f_erp_a")
    st.checkbox("Zone Inondable", key="f_erp_i")

# --- 3. PATHOLOGIES ---
elif menu == "3. Diagnostic Pathologies":
    st.subheader("⚠️ Désordres")
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "Faible", "obs": ""})
    
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            st.session_state.pathos[idx]["loc"] = st.text_input("Localisation", value=p["loc"], key=f"l_{idx}")
            st.session_state.pathos[idx]["type"] = st.selectbox("Nature", ["Fissure structurelle", "Fissure de retrait", "Humidité", "Infiltration", "Termites"], key=f"t_{idx}")
            st.session_state.pathos[idx]["grav"] = st.select_slider("Gravité", options=["Faible", "Moyenne", "Critique"], key=f"g_{idx}")
            st.session_state.pathos[idx]["obs"] = st.text_area("Observations", value=p["obs"], key=f"o_{idx}")

# --- 4. SURFACES ---
elif menu == "4. Tableau des Surfaces":
    st.subheader("📏 Relevé m²")
    if st.button("➕ Ajouter une pièce"):
        st.session_state.pieces.append({"nom": "", "surface": 0.0, "note": ""})
    for i, piece in enumerate(st.session_state.pieces):
        c1, c2, c3 = st.columns([2, 1, 2])
        st.session_state.pieces[i]["nom"] = c1.text_input("Nom de la pièce", value=piece["nom"], key=f"pnom_{i}")
        st.session_state.pieces[i]["surface"] = c2.number_input("m²", value=piece["surface"], key=f"psurf_{i}")
        st.session_state.pieces[i]["note"] = c3.text_input("Note", value=piece["note"], key=f"pnote_{i}")

# --- 5. PHOTOS ---
elif menu == "5. Photos & Signature":
    st.subheader("📸 Reportage")
    st.file_uploader("Prendre des photos", accept_multiple_files=True, type=['jpg', 'png'])
    st.text_input("Nom du signataire", key="f_sign")

# --- 6. FACTURATION ---
elif menu == "6. Facturation TTC":
    st.subheader("💰 Honoraires TTC")
    hono = st.number_input("Expertise TTC (€)", value=0.0, key="f_h_ttc")
    km = st.number_input("Nombre km (A/R)", value=0, key="f_km_ttc")
    t_km = st.number_input("Tarif TTC (€/km)", value=0.60)
    total = hono + (km * t_km)
    st.metric("TOTAL TTC", f"{total:.2f} €")
    st.session_state["total_f"] = total

# --- GÉNÉRATION DU PDF FINAL ---
st.markdown("---")
if st.button("📄 ÉDITER LE COMPTE-RENDU DE VISITE"):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # Section 1
        pdf.section_header("1. IDENTIFICATION ET TECHNIQUE")
        pdf.add_data("Client", st.session_state.get('f_donneur', 'Non renseigné'))
        pdf.add_data("Adresse", st.session_state.get('f_addr', 'Non renseignée'))
        
        # Menuiseries avec gestion de liste vide
        mat_list = st.session_state.get('f_mat_vitre', [])
        pdf.add_data("Menuiseries/Vitrages", ", ".join(mat_list) if mat_list else "Non renseigné")
        pdf.add_data("Chauffage", st.session_state.get('f_chauff', 'Non renseigné'))
        
        # Section 2
        pdf.section_header("2. PATHOLOGIES")
        if not st.session_state.pathos:
            pdf.write(5, "Aucun désordre signalé.\n".encode('latin-1'))
        else:
            for p in st.session_state.pathos:
                pdf.add_data(f"Désordre ({p['loc']})", f"{p['type']} - Gravité: {p['grav']}")

        # Section 3
        pdf.section_header("3. SYNTHESE FINANCIERE")
        pdf.add_data("TOTAL PRESTATION", f"{st.session_state.get('total_f', 0):.2f} Euros TTC")

        # Sortie sécurisée
        res = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER LE COMPTE-RENDU (PDF)", res, "Compte_Rendu_Visite.pdf", "application/pdf")
        st.success("✅ Document prêt au téléchargement.")
    except Exception as e:
        st.error(f"Une erreur est survenue lors de la création du PDF : {e}")