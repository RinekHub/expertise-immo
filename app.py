import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# --- 2. CLASSE PDF (La "machine" qui crée le document) ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 33)
        self.set_font('Arial', 'B', 14)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE', 0, 1, 'C')
        self.ln(10)

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
        val = str(value).encode('latin-1', 'replace').decode('latin-1')
        self.write(5, f"{val}\n")

# --- 3. INITIALISATION DU TABLEAU DES SURFACES ---
if 'rows' not in st.session_state:
    st.session_state.rows = 4

# --- 4. BARRE LATÉRALE (NAVIGATION) ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.title("FD Expertise")
    type_fiche = st.radio("Type de Bien", ["Appartement", "Maison"])
    st.markdown("---")
    menu = st.radio("Navigation", [
        "1. Dossier Technique", 
        "2. Risques ERP", 
        "3. Photos & Docs", 
        "4. Pathologies & Facture"
    ])

st.title(f"📋 Expertise {type_fiche}")

# Texte personnalisé pour les menus déroulants
txt_choix = "Choisissez une ou plusieurs options"

# --- 5. SECTION 1 : DOSSIER TECHNIQUE ---
if menu == "1. Dossier Technique":
    st.subheader("👤 1. Identification")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Donneur d'ordre / Client", key="f_client")
        st.text_input("Adresse du bien", key="f_adresse")
    with c2:
        st.text_input("Propriétaire", key="f_proprio")
        st.text_input("Ville / CP", key="f_ville")

    st.markdown("---")
    st.subheader("🏠 2. Caractéristiques & État Technique")
    ci1, ci2 = st.columns(2)
    with ci1:
        st.text_input("Année de construction / Rénovation", key="f_annee")
        st.text_input("Nombre d'étages / Niveaux", key="f_niveaux")
        st.selectbox("État des menuiseries", ["Excellent", "Bon état", "Moyen", "Vétuste"], key="f_etat_m")
        # LA DEMANDE : PVC Simple et Double vitrage bien listés
        st.multiselect("Type de vitrage & Matériaux", [
            "PVC Simple vitrage", "PVC Double vitrage", 
            "Aluminium Simple vitrage", "Aluminium Double vitrage", 
            "Bois Simple vitrage", "Bois Double vitrage",
            "Double vitrage phonique", "Triple vitrage", "Mixte Bois/Alu"
        ], placeholder=txt_choix, key="f_vitre")
    
    with ci2:
        if type_fiche == "Appartement":
            st.text_input("Nom du Syndic", key="f_syndic")
        else:
            is_copro = st.radio("Le bien est-il en copropriété / ASL ?", ["Non", "Oui"], horizontal=True)
            if is_copro == "Oui":
                st.text_input("Nom du Syndic / Association", key="f_syndic_m")
        
        st.selectbox("Énergie Chauffage", ["Gaz", "Électricité", "Fuel", "Pompe à chaleur", "Bois", "Solaire"], key="f_chauff")
        st.selectbox("Distribution", ["Radiateurs", "Plancher chauffant", "Clim réversible", "Convecteurs"], key="f_distri")
        st.selectbox("Situation Locative", ["Libre de toute occupation", "Occupé", "Meublé", "Saisonnier"], key="f_loc")

    st.markdown("---")
    st.subheader("📏 3. Tableau des Surfaces")
    for i in range(st.session_state.rows):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}")
        with sc2: st.number_input("m²", key=f"m{i}", step=0.01, format="%.2f")
        with sc3: st.text_input("Observations", key=f"r{i}")
    st.button("➕ Ajouter une pièce", on_click=lambda: st.session_state.update({"rows": st.session_state.rows + 1}))

# --- 6. SECTION 2 : RISQUES ERP ---
elif menu == "2. Risques ERP":
    st.subheader("🚫 État des Risques (ERP France)")
    r1, r2 = st.columns(2)
    with r1:
        st.selectbox("Zone de Sismicité", ["1 (Très faible)", "2", "3", "4", "5 (Forte)"], key="f_erp_s")
        st.selectbox("Aléa Retrait-Gonflement des Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="f_erp_a")
    with r2:
        st.checkbox("Zone Inondable (PPRI)", key="f_erp_i")
        st.checkbox("Risque Radon (Niveau 3)", key="f_erp_radon")
        st.checkbox("Plan d'Exposition au Bruit (PEB)", key="f_erp_peb")

# --- 7. SECTION 3 : PHOTOS ---
elif menu == "3. Photos & Docs":
    st.subheader("📸 Reportage Photo")
    st.file_uploader("Prendre une photo (iPad) ou Importer", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])
    st.info("Les photos seront compressées pour le rapport final.")

# --- 8. SECTION 4 : PATHOLOGIES & FACTURE ---
elif menu == "4. Pathologies & Facture":
    st.subheader("⚠️ Désordres & Pathologies")
    st.text_area("Observations détaillées de l'expert", key="f_pathos", height=150)
    
    st.markdown("---")
    st.subheader("💰 Synthèse Financière (TTC)")
    f1, f2 = st.columns(2)
    with f1:
        hono = st.number_input("Montant Honoraires Expertise TTC (€)", value=0.0)
    with f2:
        depl = st.number_input("Frais de déplacement TTC (€)", value=0.0)
    
    total_final = hono + depl
    st.metric("TOTAL GÉNÉRAL À PAYER TTC", f"{total_final:.2f} €")
    st.session_state["total_ttc"] = total_final

# --- 9. LE BOUTON DE GÉNÉRATION PDF ---
st.markdown("---")
if st.button("📄 ÉDITER LE COMPTE-RENDU DE VISITE"):
    try:
        pdf = PDF()
        pdf.add_page()
        
        # 1. Dossier Technique
        pdf.section_header("1. IDENTIFICATION DU DOSSIER")
        pdf.add_data("Client", st.session_state.get('f_client', ''))
        pdf.add_data("Adresse", st.session_state.get('f_adresse', ''))
        pdf.add_data("Ville", st.session_state.get('f_ville', ''))
        
        pdf.section_header("2. CARACTERISTIQUES TECHNIQUES")
        vitres = st.session_state.get('f_vitre', [])
        pdf.add_data("Vitrages & Materiaux", ", ".join(vitres) if vitres else "Non renseigné")
        pdf.add_data("Energie Chauffage", st.session_state.get('f_chauff', ''))
        pdf.add_data("Distribution", st.session_state.get('f_distri', ''))
        
        # 2. ERP
        pdf.section_header("3. RISQUES (ERP)")
        pdf.add_data("Sismicite", st.session_state.get('f_erp_s', ''))
        pdf.add_data("Aléa Argiles", st.session_state.get('f_erp_a', ''))

        # 3. Surfaces
        pdf.section_header("4. TABLEAU DES SURFACES")
        for i in range(st.session_state.rows):
            p_nom = st.session_state.get(f"p{i}")
            p_val = st.session_state.get(f"m{i}")
            if p_nom:
                pdf.add_data(p_nom, f"{p_val} m2")

        # 4. Facture
        pdf.section_header("5. SYNTHESE FINANCIERE")
        pdf.add_data("MONTANT TOTAL", f"{st.session_state.get('total_ttc', 0):.2f} Euros TTC")

        # Génération du flux binaire pour le téléchargement
        pdf_output = pdf.output(dest='S').encode('latin-1', 'replace')
        
        # Création du bouton de téléchargement final
        st.download_button(
            label="📥 TÉLÉCHARGER LE COMPTE-RENDU (PDF)",
            data=pdf_output,
            file_name="Compte_Rendu_Expertise.pdf",
            mime="application/pdf"
        )
        st.success("Le document a été préparé. Cliquez sur le bouton bleu ci-dessus pour l'enregistrer.")
    
    except Exception as e:
        st.error(f"Une erreur est survenue lors de la création du PDF : {e}")