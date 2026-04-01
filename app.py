import streamlit as st
import os
import json
from fpdf import FPDF
from PIL import Image
import io
import urllib.parse

# --- 1. CONFIGURATION ET STYLE ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# Fonctions de gestion des données
def save_data(name):
    data = {key: st.session_state[key] for key in st.session_state.keys()}
    if not os.path.exists("sauvegardes"): os.makedirs("sauvegardes")
    with open(f"sauvegardes/{name}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    st.success(f"✅ Dossier '{name}' sauvegardé sur le serveur.")

def load_data(name):
    try:
        with open(f"sauvegardes/{name}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for key, value in data.items(): st.session_state[key] = value
        st.info(f"📂 Dossier '{name}' chargé avec succès.")
    except: st.error("Erreur : Impossible de charger ce fichier.")

# --- 2. GÉNÉRATEUR PDF ---
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
if 'rows' not in st.session_state: st.session_state.rows = 5

# --- 4. BARRE LATÉRALE ---
with st.sidebar:
    st.header("💾 Gestion Dossiers")
    nom_dos = st.text_input("Référence Dossier", value="Expertise_001")
    c_s1, c_s2 = st.columns(2)
    with c_s1: 
        if st.button("💾 Sauver"): save_data(nom_dos)
    with c_s2:
        if os.path.exists("sauvegardes"):
            fichiers = [f.replace(".json", "") for f in os.listdir("sauvegardes") if f.endswith(".json")]
            if fichiers:
                sel = st.selectbox("Charger :", fichiers)
                if st.button("📂 Ouvrir"): load_data(sel)

    st.markdown("---")
    type_bien = st.radio("🏠 Type de Bien", ["Appartement", "Maison"])
    menu = st.radio("📍 Navigation", [
        "1. Identification & Immeuble", 
        "2. Surfaces & Annexes", 
        "3. Extérieurs & Risques", 
        "4. Pathologies (Désordres)", 
        "5. Honoraires & Calculs"
    ])

st.title(f"📋 Expertise : {type_bien}")

# --- SECTION 1 : IDENTIFICATION ET IMMEUBLE ---
if menu == "1. Identification & Immeuble":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Client & Adresse")
        st.text_input("Donneur d'ordre / Client", key="d_client")
        st.text_input("Propriétaire du bien", key="d_prop")
        adresse = st.text_input("Adresse complète", key="d_adr")
        if adresse:
            st.markdown(f"[📍 Google Maps](https://www.google.com/maps/search/{urllib.parse.quote(adresse)})")
    with col2:
        st.subheader("🏢 État Civil du Bien")
        st.text_input("Année de construction", key="i_annee")
        st.selectbox("Situation locative", ["Libre", "Occupé (Propriétaire)", "Loué (Bail en cours)", "Vides"], key="i_loc")
        st.selectbox("État général", ["Excellent / Neuf", "Bon état", "Usage normal", "À rafraîchir", "Gros travaux"], key="i_etat_gen")

    st.markdown("---")
    st.subheader(f"🛠️ Caractéristiques Techniques ({type_bien})")
    t1, t2 = st.columns(2)
    with t1:
        st.multiselect("Menuiseries / Vitrages", ["Bois", "PVC", "Alu", "Simple Vitrage", "Double Vitrage", "Volets Roulants", "Volets Battants"], key="i_menuis", placeholder="Choisir...")
        st.selectbox("Système de Chauffage", ["Gaz", "Électricité", "PAC", "Fioul", "Bois", "Collectif"], key="d_chauff")
        if type_bien == "Maison":
            st.selectbox("Assainissement", ["Tout à l'égout", "Fosse Septique", "Micro-station", "Non conforme"], key="i_assain")
        else:
            st.text_input("Étage du bien", key="i_etage")
    with t2:
        if type_bien == "Appartement":
            st.checkbox("Ascenseur disponible", key="i_asc")
            st.text_input("Nom du Syndic", key="i_syndic")
        else:
            st.text_input("Type de Toiture", key="i_toit")
            st.text_input("Surface Terrain (m²)", key="i_terrain")
            st.text_input("Nombre de niveaux (R+...)", key="i_niveaux")

# --- SECTION 2 : SURFACES ET ANNEXES ---
elif menu == "2. Surfaces & Annexes":
    st.subheader("📏 Relevé des Surfaces")
    st.info("Saisissez les pièces. Laissez vide si non utilisé.")
    for i in range(st.session_state.rows):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1: st.text_input(f"Nom de la pièce {i+1}", key=f"p{i}", placeholder="Ex: Salon")
        with sc2: st.number_input("Surface m²", key=f"m{i}", step=0.01, format="%.2f")
        with sc3: st.text_input("Observations / État du sol", key=f"r{i}", placeholder="Ex: Parquet bon état")
    st.button("➕ Ajouter une ligne", on_click=lambda: st.session_state.update({"rows": st.session_state.rows + 1}))

    st.markdown("---")
    st.subheader("📦 Annexes & Dépendances")
    list_annexes = ["Cave", "Parking", "Garage", "Grenier", "Balcon", "Terrasse", "Cellier", "Box", "Dépendance"]
    st.multiselect("Annexes présentes", list_annexes, key="a_liste", placeholder="Sélectionner les annexes...")
    st.text_area("Commentaires détaillés sur les annexes", key="a_obs")

# --- SECTION 3 : EXTÉRIEURS ET RISQUES ---
elif menu == "3. Extérieurs & Risques":
    e1, e2 = st.columns(2)
    with e1:
        st.subheader("🌳 Aménagements Extérieurs")
        if type_bien == "Maison":
            st.multiselect("Équipements", ["Jardin", "Clôture", "Portail électrique", "Piscine", "Cuisine d'été", "Puits"], key="e_amen")
            st.text_area("Observations sur le terrain", key="e_comm")
        else:
            st.write("Section réservée aux parties communes pour un appartement.")
            st.text_area("Observations Parties Communes", key="e_comm")
    with e2:
        st.subheader("🚫 Risques (ERP)")
        st.selectbox("Zone Sismique", ["1 (Très faible)", "2 (Faible)", "3 (Modéré)", "4 (Moyen)", "5 (Fort)"], key="e_sis")
        st.selectbox("Retrait-Gonflement Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="e_arg")
        st.checkbox("Zone Inondable", key="e_inond")
        st.checkbox("Exposition Radon", key="e_radon")

# --- SECTION 4 : PATHOLOGIES ---
elif menu == "4. Pathologies (Désordres)":
    st.subheader("⚠️ Diagnostic des Désordres & Pathologies")
    if st.button("➕ Ajouter un nouveau désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢 Faible", "obs": ""})
    
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1} : {p.get('type', 'Inconnu')}", expanded=True):
            c_p1, c_p2 = st.columns(2)
            with c_p1:
                p["loc"] = st.text_input("Localisation précise", key=f"ploc_{idx}", value=p.get("loc", ""))
                p["type"] = st.selectbox("Nature du désordre", ["Fissure", "Humidité / Salpêtre", "Infiltration", "Affaissement structurel", "Oxydation"], key=f"ptyp_{idx}")
            with c_p2:
                p["grav"] = st.select_slider("Gravité", options=["🟢 Faible", "🟡 Moyenne", "🔴 Critique"], key=f"pgrav_{idx}")
            p["obs"] = st.text_area("Description et préconisations", key=f"pobs_{idx}", value=p.get("obs", ""))
            if st.button(f"🗑️ Supprimer désordre n°{idx+1}", key=f"del_{idx}"):
                st.session_state.pathos.pop(idx)
                st.rerun()

# --- SECTION 5 : HONORAIRES ET CALCULS ---
elif menu == "5. Honoraires & Calculs":
    st.subheader("💰 Facturation & Frais de déplacement")
    f1, f2 = st.columns(2)
    with f1:
        h_ttc = st.number_input("Honoraires Expertise TTC (€)", value=0.0, key="h_val")
        dist = st.number_input("Distance parcourue A/R (KM)", value=0, key="dist_val")
    with f2:
        t_km = st.number_input("Tarif Kilométrique TTC (€/km)", value=0.60, key="tk_val")
    
    ik_total = dist * t_km
    total_general = h_ttc + ik_total
    
    st.markdown("---")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.metric("TOTAL GÉNÉRAL TTC", f"{total_general:.2f} €")
    with c_m2:
        st.metric("Dont IK (Déplacement)", f"{ik_total:.2f} €")
    
    st.info(f"Montant HT estimé (TVA 20%) : {total_general/1.2:.2f} €")
    st.session_state["final_ttc"] = total_general

# --- 5. GÉNÉRATION DU PDF FINAL ---
st.markdown("---")
if st.button("📄 GÉNÉRER LE COMPTE-RENDU PDF"):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # Section 1
        pdf.section_header(1, f"IDENTIFICATION DU BIEN ({type_bien.upper()})")
        pdf.add_data("Client", st.session_state.get('d_client'))
        pdf.add_data("Adresse", st.session_state.get('d_adr'))
        pdf.add_data("Situation Locative", st.session_state.get('i_loc'))
        if type_bien == "Appartement":
            pdf.add_data("Etage / Ascenseur", f"{st.session_state.get('i_etage')} / {st.session_state.get('i_asc')}")
        else:
            pdf.add_data("Assainissement", st.session_state.get('i_assain'))

        # Section 2
        pdf.section_header(2, "SURFACES ET ANNEXES")
        for i in range(st.session_state.rows):
            p_n = st.session_state.get(f"p{i}")
            if p_n:
                pdf.add_data(p_n, f"{st.session_state.get(f'm{i}')} m2 - {st.session_state.get(f'r{i}')}")
        annexes = st.session_state.get('a_liste', [])
        pdf.add_data("Annexes", ", ".join(annexes) if annexes else "Néant")

        # Section 3
        pdf.section_header(3, "PATHOLOGIES ET DÉSORDRES")
        if not st.session_state.pathos:
            pdf.add_data("Désordres", "Aucun désordre apparent lors de la visite.")
        for p in st.session_state.pathos:
            pdf.add_data(f"Désordre {p['type']} ({p['grav']})", f"Lieu: {p['loc']} - Obs: {p['obs']}")

        # Section 4
        pdf.section_header(4, "SYNTHÈSE FINANCIÈRE")
        pdf.add_data("TOTAL TTC DES HONORAIRES", f"{st.session_state.get('final_ttc', 0):.2f} Euros")

        # Sortie
        res = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER LE RAPPORT PDF", res, f"Expertise_{nom_dos}.pdf", "application/pdf")
        
    except Exception as e:
        st.error(f"Une erreur est survenue lors de la création du PDF : {e}")