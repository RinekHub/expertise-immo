import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# Initialisation
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 5

# --- 2. CLASSE PDF (POLICE & LOGO D'ORIGINE) ---
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
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE', 0, 1, 'C')
        self.ln(5)

    def section_header(self, label):
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(230, 230, 230)
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

# --- 3. BARRE LATÉRALE (LOGO FD EN PREMIER) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    st.markdown("---")
    type_bien = st.radio("🏠 Type de Bien", ["Appartement", "Maison"], key="type_bien")
    st.markdown("---")
    if st.button("🗑️ NOUVEAU DOSSIER (RESET)"):
        st.session_state.clear()
        st.rerun()

st.title(f"Expertise : {type_bien}")

# --- SECTION 1 : DOSSIER & TECHNIQUE ---
st.header("📁 1. Section Dossier & Technique")
c1, c2 = st.columns(2)
with c1:
    st.subheader("👤 Identification")
    st.text_input("Donneur d'ordre", key="d_client")
    st.text_input("Propriétaire", key="d_prop")
    st.text_input("Adresse du bien", key="d_adr")
with c2:
    # 1. Le titre qui change selon le bien (Maison ou Immeuble)
    titre_bloc = "🏠 Bloc Maison" if type_bien == "Maison" else "🏢 Bloc Immeuble"
    st.subheader(titre_bloc)
    
    # 2. Le Facteur Année (ton critère important)
    st.text_input("Facteur Année", key="i_annee")
    
    # 3. La Situation Locative en Français ("Choisissez...")
    st.selectbox("Situation Locative", ["Libre", "Occupé (Proprio)", "Loué", "Vides"], index=None, placeholder="Choisissez...", key="i_loc")
    
    # 4. La logique conditionnelle (Syndic pour Appart / Copro pour Maison)
    if type_bien == "Appartement":
        st.text_input("Syndic (Nom / Contact)", key="i_syndic")
        st.checkbox("Ascenseur", key="i_asc")
    else:
        # Pour le formulaire Maison, on demande si c'est en copropriété ou non
        st.radio("Régime de propriété", ["Non (Pleine Propriété)", "Oui (Maison en Copropriété)"], key="i_copro_m")

st.markdown("---")

# --- SECTION 2 : MENUISERIES & ÉNERGIES ---
st.header("🏠 2. Menuiseries & Énergies")
m1, m2 = st.columns(2)
with m1:
    st.multiselect("Matériaux", ["PVC", "Alu", "Bois", "Mixte"], placeholder="Choisissez...", key="m_mat")
    st.selectbox("Type de vitrage", ["Simple vitrage", "Double vitrage", "Double vitrage FE", "Triple vitrage"], key="m_vitre")
    st.selectbox("État des menuiseries", ["Bon", "Moyen", "Vétuste"], key="m_etat")
with m2:
    st.selectbox("Source d'énergie", ["Électricité", "Gaz Naturel", "PAC", "Fuel", "Chaudière électrique", "Bois"], key="e_source")
    st.selectbox("Production Eau Chaude", ["Cumulus électrique", "Ballon Thermo", "Chaudière mixte", "Chaudière Fuel"], key="e_eau")

st.markdown("---")

# --- SECTION 3 : EXTÉRIEURS & RISQUES (ERP) ---
st.header("🌳 3. Section Extérieurs & Risques")
e1, e2 = st.columns(2)
with e1:
    st.subheader("🌳 Aménagements & Annexes")
    
    # Éléments communs (Appartement et Maison)
    st.multiselect("Annexes du bien", 
                   ["Terrasse", "Balcon", "Véranda", "Loggia", "Cave", "Parking / Box", "Cellier"], 
                   placeholder="Choisissez...", 
                   key="a_annexes")
    
    # Options spécifiques si c'est une Maison
    if type_bien == "Maison":
        st.text_input("Terrain (Clôture, Puits, Haies, Portail)", key="t_terrain")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"], index=None, placeholder="Choisissez...", key="t_piscine")
        st.multiselect("Équipements Extérieurs", ["Arrosage auto", "Éclairage", "Cuisine d'été", "Abri jardin"], placeholder="Choisissez...", key="t_equip")
    
    # État général (Pour tous)
    st.selectbox("État d'entretien général", 
                 ["Excellent", "Bon", "Moyen", "Négligé"], 
                 index=None, 
                 placeholder="Choisissez...", 
                 key="i_entretien")
with e2:
    st.subheader("🚫 Risques (ERP)")
    st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="erp_sis")
    st.selectbox("Aléa Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="erp_arg")
    st.checkbox("Zone inondable", key="erp_inond")

st.markdown("---")

# --- SECTION 4 : PATHOLOGIES ---
st.header("⚠️ 4. Section Pathologies")
if st.button("➕ Ajouter un désordre"):
    st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢 Faible", "obs": ""})
    st.rerun()

for idx, p in enumerate(st.session_state.pathos):
    with st.expander(f"⚠️ Désordre n°{idx+1}", expanded=True):
        col_p1, col_p2 = st.columns(2)
        
        with col_p1:
            # 1. Localisation (ex: Façade Nord, Salon...)
            st.session_state.pathos[idx]["loc"] = st.text_input("Localisation du désordre", 
                                                               key=f"ploc_{idx}", 
                                                               value=p["loc"])
            
            # 2. LA LISTE DES DÉSORDRES (Le menu qui manquait)
            st.session_state.pathos[idx]["type"] = st.selectbox("Nature du désordre", 
                                                               ["Fissure structurelle", "Fissure esthétique", "Humidité / Salpêtre", "Infiltration toiture", "Défaut d'étanchéité", "Remontée capillaire", "Affaissement", "Autre"], 
                                                               index=None, 
                                                               placeholder="Choisissez...", 
                                                               key=f"ptyp_{idx}")
        
        with col_p2:
            # 3. La Gravité (Slider visuel)
            st.session_state.pathos[idx]["grav"] = st.select_slider("Degré de gravité", 
                                                                   options=["🟢 Faible", "🟡 Modéré", "🔴 Grave"], 
                                                                   key=f"pgrav_{idx}", 
                                                                   value=p["grav"])
        
        # 4. Observations avec dictée vocale
        st.session_state.pathos[idx]["obs"] = st.text_area("Observations détaillées (🎙️ Dictée possible)", 
                                                          key=f"pobs_{idx}", 
                                                          value=p["obs"])
        
        # Bouton pour supprimer si erreur
        if st.button(f"🗑️ Supprimer ce désordre", key=f"del_{idx}"):
            st.session_state.pathos.pop(idx)
            st.rerun()

st.markdown("---")

# --- SECTION 5 : SURFACES (BAS DE PAGE) ---
st.header("📏 5. Tableau des Surfaces")
for i in range(st.session_state.rows):
    sc1, sc2, sc3 = st.columns([2, 1, 2])
    with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
    with sc2: st.number_input("m²", key=f"m{i}", step=0.01)
    with sc3: st.text_input("Obs/État", key=f"r{i}")
if st.button("➕ Ajouter une ligne"):
    st.session_state.rows += 1
    st.rerun()

st.markdown("---")

# --- SECTION 6 : PHOTOS & SIGNATURE ---
st.header("📸 6. Photos & Signature")
st.file_uploader("📸 Ajouter des photos", accept_multiple_files=True, key="photos_fin")
st.text_area("Note de synthèse / Commentaires libres", key="comm_libres")
st.text_input("🖋️ Signature (Nom du signataire)", key="signature_nom")

st.markdown("---")

# --- SECTION 7 : FACTURATION ---
st.header("💶 7. Facturation TTC")
f1, f2, f3 = st.columns(3)
with f1: h_ttc = st.number_input("Hono TTC (€)", key="h_val")
with f2: dist = st.number_input("KM (A/R)", key="dist_val")
with f3: t_km = st.number_input("Tarif KM", value=0.60, key="tk_val")
total = h_ttc + (dist * t_km)
st.metric("TOTAL GÉNÉRAL TTC", f"{total:.2f} €")

# --- BOUTON PDF FINAL ---
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
        st.download_button("📥 TÉLÉCHARGER LE PDF", buf, "Rapport_FD.pdf", "application/pdf")
    except Exception as e: st.error(f"Erreur : {e}")