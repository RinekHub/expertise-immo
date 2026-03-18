import streamlit as st
import os
from fpdf import FPDF

# --- CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

class FD_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 10, 'CABINET FD EXPERTISE - FICHE TECHNIQUE CONFIDENTIELLE', ln=True, align='L')
        self.ln(5)

def create_pdf(data, pieces, type_bien):
    pdf = FD_PDF()
    pdf.add_page()
    
    # Titre
    pdf.set_font("Arial", 'B', 14)
    titre = f"FICHE TECHNIQUE : VISITE {'APPARTEMENT' if type_bien == 'Appt' else 'MAISON'}"
    pdf.cell(0, 10, titre, ln=True, align='C')
    pdf.ln(5)

    # Sections classiques
    for section, content in data.items():
        pdf.set_font("Arial", 'B', 11)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, section, ln=True, fill=True)
        pdf.set_font("Arial", '', 9)
        for key, value in content.items():
            pdf.cell(95, 6, f"{key}: {value}", border=0)
            if list(content.keys()).index(key) % 2 != 0: pdf.ln(6)
        pdf.ln(4)

    # TABLEAU DES SURFACES
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "DETAIL DES SURFACES (LOI CARREZ / HABITABLE)", ln=True, fill=True)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(80, 7, "Piece", border=1)
    pdf.cell(40, 7, "Surface (m2)", border=1)
    pdf.cell(70, 7, "Revetements / Observations", border=1, ln=True)
    
    pdf.set_font("Arial", '', 9)
    total_surf = 0
    for p in pieces:
        if p["nom"]:
            pdf.cell(80, 7, p["nom"], border=1)
            pdf.cell(40, 7, str(p["surf"]), border=1)
            pdf.cell(70, 7, p["obs"], border=1, ln=True)
            total_surf += p["surf"]
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(80, 7, "TOTAL SURFACE CALCULEE", border=1)
    pdf.cell(40, 7, f"{total_surf:.2f} m2", border=1, ln=True)

    return pdf.output(dest='S').encode('latin-1', errors='replace')

# --- INTERFACE ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    type_fiche = st.radio("Type de Bien", ["Appt", "M"])
    st.markdown("---")
    st.write("📌 *Note : Pensez à enregistrer avant de générer le PDF.*")

st.title(f"🏢 Expertise {type_fiche} - Saisie de terrain")

# 1. INFOS GENERALES
col_a, col_b = st.columns(2)
with col_a:
    donneur = st.text_input("Donneur d'ordre", value="M. et Mme")
    adresse = st.text_input("Adresse du bien")
with col_b:
    proprio = st.text_input("Propriétaire")
    cadastre = st.text_input("Section / Parcelles")

# 2. TABLEAU DYNAMIQUE DES PIÈCES
st.subheader("📏 Tableau des Surfaces")
st.write("Entrez le nom de la pièce et sa surface. Le total se calcule en bas.")

if 'nb_pieces' not in st.session_state:
    st.session_state.nb_pieces = 5

def ajouter_piece(): st.session_state.nb_pieces += 1

pieces_data = []
for i in range(st.session_state.nb_pieces):
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1: nom = st.text_input(f"Pièce {i+1}", key=f"n{i}", placeholder="ex: Salon")
    with c2: surf = st.number_input("m²", key=f"s{i}", step=0.01, min_value=0.0)
    with c3: obs = st.text_input("Revêtement/État", key=f"o{i}", placeholder="Parquet / Bon état")
    pieces_data.append({"nom": nom, "surf": surf, "obs": obs})

st.button("➕ Ajouter une ligne", on_click=ajouter_piece)

total_m2 = sum(p["surf"] for p in pieces_data)
st.info(f"**Surface totale saisie : {total_m2:.2f} m²**")

# 3. ÉQUIPEMENTS TECHNIQUES
st.subheader("🛠️ Caractéristiques Techniques")
t1, t2, t3 = st.columns(3)
with t1:
    chauffage = st.selectbox("Chauffage", ["Individuel", "Collectif"])
    energie = st.text_input("Énergie (Gaz, Elec...)")
with t2:
    menuiserie = st.selectbox("Menuiseries", ["PVC Double Vitrage", "Bois Simple", "Alu"])
    dpe = st.select_slider("DPE", options=["A", "B", "C", "D", "E", "F", "G"])
with t3:
    if type_fiche == "Appt":
        etage = st.text_input("Étage / Ascenseur")
        lots = st.text_input("Numéro de Lot(s)")
    else:
        assainissement = st.text_input("Assainissement")
        facade = st.text_input("État Façade")

# 4. BOUTON FINAL
if st.button("🚀 GÉNÉRER LA FICHE PDF"):
    data_pdf = {
        "IDENTIFICATION": {"Donneur": donneur, "Proprio": proprio, "Adresse": adresse, "Cadastre": cadastre},
        "TECHNIQUE": {"Chauffage": chauffage, "Energie": energie, "DPE": dpe, "Menuiseries": menuiserie}
    }
    if type_fiche == "Appt":
        data_pdf["COPROPRIETE"] = {"Etage/Asc": etage, "Lots": lots}
    else:
        data_pdf["EXTERIEUR"] = {"Assainissement": assainissement, "Facade": facade}
    
    pdf_bytes = create_pdf(data_pdf, pieces_data, type_fiche)
    
    st.success("PDF Prêt !")
    st.download_button("⬇️ Télécharger maintenant", data=pdf_bytes, file_name=f"Expertise_{type_fiche}.pdf")