import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- 2. CLASSE PDF ---
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

# --- 3. INITIALISATION CRUCIALE ---
# On s'assure que ces boîtes existent au démarrage pour ne jamais les vider
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 5
if 'type_bien' not in st.session_state: st.session_state.type_bien = "Appartement"

# --- 4. BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=150)
    st.markdown("---")
    
    # On stocke le type de bien directement dans la session
    st.radio("🏠 Type de Bien", ["Appartement", "Maison"], key="type_bien")
    
    st.markdown("---")
    menu = st.radio("📍 Navigation", ["📝 1. Expertise Technique", "💰 2. Facturation & PDF"])
    
    st.markdown("---")
    if st.button("🗑️ TOUT EFFACER (Nouveau Dossier)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Récupération simplifiée pour le reste du code
type_bien = st.session_state.type_bien

# --- PAGE 1 : EXPERTISE ---
if menu == "📝 1. Expertise Technique":
    st.title(f"📋 Expertise : {type_bien}")
    
    st.subheader("1. Dossier & Immeuble")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Donneur d'ordre", key="d_client")
        st.text_input("Adresse du bien", key="d_adr")
        st.text_input("Propriétaire", key="d_prop")
    with c2:
        st.text_input("Année de construction", key="i_annee")
        st.selectbox("Situation locative", ["Libre", "Occupé", "Loué", "Vides"], key="i_loc")
        if type_bien == "Appartement":
            st.text_input("Étage", key="i_etage")
            st.text_input("Nom du Syndic", key="i_syndic")
        else:
            st.selectbox("Assainissement", ["Tout à l'égout", "Fosse Septique", "Micro-station"], key="i_assain")
            st.text_input("Surface Terrain (m²)", key="i_terrain")

    st.markdown("---")
    st.subheader("2. Surfaces & Annexes")
    for i in range(st.session_state.rows):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
        with sc2: st.number_input("m²", key=f"m{i}", step=0.01, format="%.2f")
        with sc3: st.text_input("Observations", key=f"r{i}")
    
    if st.button("➕ Ajouter une pièce"):
        st.session_state.rows += 1
        st.rerun()

    st.multiselect("Annexes présentes", ["Garage", "Cave", "Parking", "Balcon", "Terrasse", "Grenier"], key="a_liste")

    st.markdown("---")
    st.subheader("3. Extérieurs & Risques")
    ec1, ec2 = st.columns(2)
    with ec1:
        if type_bien == "Maison":
            st.multiselect("Équipements", ["Jardin", "Clôture", "Portail élec", "Piscine"], key="e_amen")
        st.text_area("Observations terrain / Parties Communes", key="e_comm")
    with ec2:
        st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="e_sis")
        st.checkbox("Zone inondable", key="e_inond")

    st.markdown("---")
    st.subheader("4. Pathologies")
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢", "obs": ""})
        st.rerun()

    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            # Ici on lie directement à la liste dans la session
            st.session_state.pathos[idx]["loc"] = st.text_input("Localisation", key=f"ploc_{idx}", value=p["loc"])
            st.session_state.pathos[idx]["type"] = st.selectbox("Type", ["Fissure", "Humidité", "Structure", "Infiltration"], key=f"ptyp_{idx}", index=["Fissure", "Humidité", "Structure", "Infiltration"].index(p["type"]))
            st.session_state.pathos[idx]["grav"] = st.select_slider("Gravité", options=["🟢", "🟡", "🔴"], key=f"pgrav_{idx}", value=p["grav"])
            st.session_state.pathos[idx]["obs"] = st.text_area("Observations", key=f"pobs_{idx}", value=p["obs"])
            if st.button(f"🗑️ Supprimer n°{idx+1}", key=f"del_{idx}"):
                st.session_state.pathos.pop(idx)
                st.rerun()

# --- PAGE 2 : FACTURATION ---
elif menu == "💰 2. Facturation & PDF":
    st.title("💰 Finalisation")
    
    f1, f2, f3 = st.columns(3)
    with f1: h_ttc = st.number_input("Honoraires TTC (€)", key="h_val")
    with f2: dist = st.number_input("Distance KM (A/R)", key="dist_val")
    with f3: t_km = st.number_input("Tarif KM (€)", value=0.60, key="tk_val")
    
    total_calc = h_ttc + (dist * t_km)
    st.metric("TOTAL GÉNÉRAL TTC", f"{total_calc:.2f} €")

    st.markdown("---")
    if st.button("📄 GÉNÉRER LE RAPPORT PDF"):
        try:
            pdf = PDF()
            pdf.add_page()
            pdf.section_header(f"IDENTIFICATION ({type_bien.upper()})")
            pdf.add_data("Client", st.session_state.get('d_client', ''))
            pdf.add_data("Adresse", st.session_state.get('d_adr', ''))
            
            pdf.section_header("SURFACES")
            for i in range(st.session_state.rows):
                p_n = st.session_state.get(f"p{i}")
                if p_n: pdf.add_data(p_n, f"{st.session_state.get(f'm{i}', 0.0)} m2")
            
            if st.session_state.pathos:
                pdf.section_header("PATHOLOGIES")
                for p in st.session_state.pathos:
                    pdf.add_data(f"{p['type']} ({p['grav']})", f"{p['loc']} : {p['obs']}")

            pdf.section_header("FINANCES")
            pdf.add_data("TOTAL TTC", f"{total_calc:.2f} Euros")

            res = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📥 TÉLÉCHARGER LE PDF", res, "Expertise_FD.pdf", "application/pdf")
        except Exception as e: st.error(f"Erreur : {e}")