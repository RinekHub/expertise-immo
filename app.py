import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io
import urllib.parse

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- 2. CLASSE PDF PROFESSIONNELLE ---
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
            except:
                self.set_font('Arial', 'B', 12)
                self.cell(0, 10, 'CABINET FD EXPERTISE', 0, 1, 'L')
        else:
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'CABINET FD EXPERTISE', 0, 1, 'L')
        
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
    # Ajout de la key pour garder le choix Maison/Appart
    type_bien = st.radio("🏠 Type de Bien", ["Appartement", "Maison"], key="type_bien_permanent")
    st.markdown("---")
    menu = st.radio("📍 Navigation", [
        "1. Dossier & Immeuble", 
        "2. Surfaces & Annexes", 
        "3. Extérieurs & Risques", 
        "4. Pathologies", 
        "5. Facturation"
    ])
    st.markdown("---")
    if st.button("🗑️ EFFACER TOUT LE FORMULAIRE", help="Action RGPD : Vide tout"):
        st.session_state.clear()
        st.rerun()

st.title(f"📋 Expertise : {type_bien}")

# --- SECTION 1 : DOSSIER & IMMEUBLE ---
if menu == "1. Dossier & Immeuble":
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👤 Identification")
        st.text_input("Donneur d'ordre", key="d_client")
        st.text_input("Adresse du bien", key="d_adr")
        st.text_input("Propriétaire", key="d_prop")
    with c2:
        st.subheader("🏢 Caractéristiques")
        st.text_input("Année de construction", key="i_annee")
        st.selectbox("Situation locative", ["Libre", "Occupé (Proprio)", "Loué", "Vides"], key="i_loc")
        if type_bien == "Appartement":
            st.text_input("Étage", key="i_etage")
            st.checkbox("Ascenseur", key="i_asc")
            st.text_input("Syndic", key="i_syndic")
        else:
            st.selectbox("Assainissement", ["Tout à l'égout", "Fosse Septique", "Micro-station"], key="i_assain")
            st.text_input("Type de toiture", key="i_toit")
            st.text_input("Terrain (m²)", key="i_terrain")
    
    st.markdown("---")
    st.multiselect("État des menuiseries", ["Bois", "Alu", "PVC Simple","PVC Double"], key="i_menuis", placeholder="Choisir...")
    st.selectbox("État général", ["Très bon", "Bon", "Usage normal", "À rénover"], key="i_etat_gen")

# --- SECTION 2 : SURFACES & ANNEXES ---
elif menu == "2. Surfaces & Annexes":
    st.subheader("📏 Tableau des Surfaces (m²)")
    for i in range(st.session_state.rows):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
        with sc2: st.number_input("m²", key=f"m{i}", step=0.01)
        with sc3: st.text_input("État/Observations", key=f"r{i}")
    st.button("➕ Ajouter une pièce", on_click=lambda: st.session_state.update({"rows": st.session_state.rows + 1}))

    st.markdown("---")
    st.subheader("📦 Annexes")
    annexes_liste = ["Garage", "Cave", "Parking", "Balcon", "Terrasse", "Grenier", "Abri jardin"]
    st.multiselect("Annexes présentes", annexes_liste, key="a_liste", placeholder="Choisir...")
    st.text_area("Observations détaillées annexes", key="a_obs")

# --- SECTION 3 : EXTÉRIEURS & RISQUES ---
elif menu == "3. Extérieurs & Risques":
    e1, e2 = st.columns(2)
    with e1:
        st.subheader("🏡 Extérieurs")
        if type_bien == "Maison":
            st.multiselect("Équipements", ["Jardin", "Clôture", "Portail élec", "Piscine"], key="e_amen")
            st.text_area("Observations terrain", key="e_comm")
        else:
            st.write("Section parties communes.")
            st.text_area("Observations PC", key="e_comm")
    with e2:
        st.subheader("🚫 Risques (ERP)")
        st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="e_sis")
        st.selectbox("Aléa Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="e_arg")
        st.checkbox("Zone inondable", key="e_inond")

# --- SECTION 4 : PATHOLOGIES ---
elif menu == "4. Pathologies":
    st.subheader("⚠️ Désordres")
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢", "obs": ""})
    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            # On lie directement les valeurs à la liste pour la persistance
            st.session_state.pathos[idx]["loc"] = st.text_input("Localisation", key=f"ploc_{idx}", value=p["loc"])
            st.session_state.pathos[idx]["type"] = st.selectbox("Type", ["Fissure", "Humidité", "Structure", "Infiltration"], key=f"ptyp_{idx}", index=["Fissure", "Humidité", "Structure", "Infiltration"].index(p["type"]))
            st.session_state.pathos[idx]["grav"] = st.select_slider("Gravité", options=["🟢", "🟡", "🔴"], key=f"pgrav_{idx}", value=p["grav"])
            st.session_state.pathos[idx]["obs"] = st.text_area("Observations", key=f"pobs_{idx}", value=p["obs"])
            if st.button(f"🗑️ Supprimer n°{idx+1}", key=f"del_{idx}"):
                st.session_state.pathos.pop(idx)
                st.rerun()

# --- SECTION 5 : FACTURATION ---
elif menu == "5. Facturation":
    st.subheader("💰 Honoraires & KM")
    f1, f2 = st.columns(2)
    with f1:
        h_ttc = st.number_input("Hono TTC (€)", key="h_val")
        dist = st.number_input("Distance KM (A/R)", key="dist_val")
    with f2:
        t_km = st.number_input("Tarif KM", value=0.60, key="tk_val")
    total = h_ttc + (dist * t_km)
    st.metric("TOTAL GÉNÉRAL TTC", f"{total:.2f} €")
    st.session_state["final_ttc"] = total

# --- GÉNÉRATION PDF (TON SOCLE INTACT) ---
st.markdown("---")
if st.button("📄 GÉNÉRER LE RAPPORT PDF"):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.section_header(f"IDENTIFICATION ({type_bien.upper()})")
        pdf.add_data("Client", st.session_state.get('d_client'))
        pdf.add_data("Adresse", st.session_state.get('d_adr'))
        if type_bien == "Appartement":
            pdf.add_data("Etage", st.session_state.get('i_etage'))
        else:
            pdf.add_data("Terrain", st.session_state.get('i_terrain'))
        
        pdf.section_header("SURFACES")
        for i in range(st.session_state.rows):
            p_n = st.session_state.get(f"p{i}")
            if p_n: pdf.add_data(p_n, f"{st.session_state.get(f'm{i}')} m2 - {st.session_state.get(f'r{i}')}")

        pdf.section_header("PATHOLOGIES")
        for p in st.session_state.pathos:
            pdf.add_data(f"{p['type']} ({p['grav']})", f"{p['loc']} : {p['obs']}")

        pdf.section_header("FINANCES")
        pdf.add_data("TOTAL TTC", f"{st.session_state.get('final_ttc', 0):.2f} Euros")

        res = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER", res, "Expertise_FD.pdf", "application/pdf")
    except Exception as e: