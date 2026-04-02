import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURATION & MÉMOIRE ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 5

# --- 2. FONCTION DE CHARGEMENT LOGO SÉCURISÉE ---
def charger_logo():
    """Charge le logo depuis le disque et le convertit pour FPDF"""
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path)
            # FIX : Conversion RGBA/Palette et Interlacing vers RGB (JPEG compatible)
            if img.mode in ("RGBA", "P") or img.info.get("interlace"):
                img = img.convert("RGB")
            
            # Buffer mémoire pour éviter les fichiers temporaires
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='JPEG')
            img_buffer.seek(0)
            return img_buffer
        except Exception as e:
            st.warning(f"⚠️ Erreur technique lors du chargement du logo : {e}")
            return None
    else:
        # L'ERREUR VIENT D'ICI : Le fichier n'est pas sur le serveur Streamlit
        st.error("❌ Fichier 'logo.png' introuvable dans le dossier du projet sur GitHub.")
        st.info("💡 Pour régler ça : Ajoute ton fichier 'logo.png' sur ton dépôt GitHub, à côté de 'app.py'.")
        return None

# --- 3. CLASSE PDF (UTILISE LE LOGO STABLE) ---
class PDF(FPDF):
    def header(self):
        # On tente de charger le logo stable
        logo_data = charger_logo()
        if logo_data:
            try:
                self.image(logo_data, 10, 8, 33)
                self.ln(15)
            except Exception as e:
                st.warning(f"Note : Impossible d'insérer le logo dans le PDF ({e})")
        
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'COMPTE-RENDU DE VISITE TECHNIQUE D\'EXPERTISE', 0, 1, 'C')
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

# --- 4. BARRE LATÉRALE ---
with st.sidebar:
    st.header("📸 Photos & Documents")
    st.file_uploader("Prendre photo / Bibliothèque", accept_multiple_files=True, key="photos_up")
    st.markdown("---")
    type_bien = st.radio("🏠 Type de Bien", ["Appartement", "Maison"], key="type_bien")
    st.markdown("---")
    if st.button("🗑️ NOUVEAU DOSSIER (RGPD)"):
        st.session_state.clear()
        st.rerun()

st.title(f"Expertise FD : {type_bien}")

# --- SECTION 1 : DOSSIER & TECHNIQUE ---
st.header("1. Section Dossier & Technique")
c1, c2 = st.columns(2)
with c1:
    st.subheader("👤 Identification")
    st.text_input("Donneur d'ordre", key="d_client")
    st.text_input("Propriétaire", key="d_prop")
    adr = st.text_input("Adresse du bien", key="d_adr")
    if adr:
        st.markdown(f"[🔗 Google Maps](http://googleusercontent.com/maps.google.com/2{adr.replace(' ', '+')})")
with c2:
    st.subheader("🏢 Bloc Immeuble")
    st.text_input("Facteur Année (Const./Rénov.)", key="i_annee")
    st.selectbox("Situation Locative", ["Libre", "Occupé (Proprio)", "Loué", "Vides"], key="i_loc")
    if type_bien == "Appartement":
        st.text_input("Étage", key="i_etage")
        st.text_input("Syndic", key="i_syndic")
        st.checkbox("Ascenseur", key="i_asc")
    else:
        st.radio("Copropriété ?", ["Non (Pleine Propriété)", "Oui (Horizontale)"], key="i_copro_m")

st.markdown("---")

# --- SECTION 2 : MENUISERIES & ÉNERGIE ---
st.header("2. Menuiseries & Énergies")
m1, m2 = st.columns(2)
with m1:
    st.subheader("🪟 Menuiseries")
    st.multiselect("Matériaux", ["PVC", "Alu", "Bois", "Mixte"], key="m_mat")
    st.selectbox("Type de vitrage", ["Simple vitrage", "Double vitrage", "Double vitrage FE", "Triple vitrage"], key="m_vitre")
    st.selectbox("État", ["Bon", "Moyen", "Vétuste"], key="m_etat")
with m2:
    st.subheader("🔥 Chauffage & Eau Chaude")
    st.selectbox("Source d'énergie", ["Électricité", "Gaz Naturel", "Gaz Citerne", "PAC", "Fuel", "Chaudière électrique", "Bois"], key="e_source")
    st.selectbox("Production Eau Chaude", ["Cumulus électrique", "Ballon Thermo", "Chaudière mixte", "Fuel"], key="e_eau")

st.markdown("---")

# --- SECTION 3 : EXTÉRIEURS & RISQUES ---
st.header("3. Section Extérieurs & Risques")
e1, e2 = st.columns(2)
with e1:
    st.subheader("🏡 Aménagements")
    if type_bien == "Maison":
        st.text_input("Clôture / Haies", key="t_cloture")
        st.multiselect("Équipements", ["Puits", "Forage", "Éclairage", "Arrosage"], key="t_equip")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"], key="t_piscine")
        st.multiselect("Sécurité Piscine", ["Alarme", "Volet", "Barrière", "Couverture"], key="t_pisc_secu")
    st.selectbox("Entretien Général", ["Excellent", "Bon", "Moyen", "Négligé"], key="i_entretien")
with e2:
    st.subheader("🚫 Risques (ERP)")
    st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="erp_sis")
    st.selectbox("Aléa Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="erp_arg")
    st.checkbox("Zone inondable", key="erp_inond")

st.markdown("---")

# --- SECTION 4 : PATHOLOGIES ---
st.header("4. Section Pathologies")
if st.button("➕ Ajouter un désordre"):
    st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢 Faible", "obs": ""})
    st.rerun()

for idx, p in enumerate(st.session_state.pathos):
    with st.expander(f"Désordre n°{idx+1}", expanded=True):
        st.session_state.pathos[idx]["loc"] = st.text_input("Localisation", key=f"ploc_{idx}", value=p["loc"])
        st.session_state.pathos[idx]["grav"] = st.select_slider("Gravité", options=["🟢 Faible", "🟡 Modéré", "🔴 Grave"], key=f"pgrav_{idx}", value=p["grav"])
        st.session_state.pathos[idx]["obs"] = st.text_area("Observations (🎙️)", key=f"pobs_{idx}", value=p["obs"])
        if st.button(f"🗑️ Supprimer n°{idx+1}", key=f"del_{idx}"):
            st.session_state.pathos.pop(idx)
            st.rerun()

st.markdown("---")

# --- SECTION 5 : SURFACES ---
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

# --- SECTION 6 : SIGNATURE & FACTURE ---
st.header("6. Synthèse & Facturation")
st.text_area("Commentaires Libres", key="comm_libres")
st.text_input("Nom du signataire (Signature iPad)", key="signature_nom")

f1, f2, f3 = st.columns(3)
with f1: h_ttc = st.number_input("Hono TTC (€)", key="h_val")
with f2: dist = st.number_input("KM (A/R)", key="dist_val")
with f3: t_km = st.number_input("Tarif KM", value=0.60, key="tk_val")

total = h_ttc + (dist * t_km)
st.metric("TOTAL GÉNÉRAL TTC", f"{total:.2f} €")

# --- BOUTON PDF ---
if st.button("📄 ÉDITER LE COMPTE-RENDU FINAL"):
    try:
        pdf = PDF()
        pdf.add_page()
        pdf.section_header("Identification")
        pdf.add_data("Client", st.session_state.get('d_client'))
        pdf.add_data("Adresse", st.session_state.get('d_adr'))
        
        pdf.section_header("Surfaces")
        for i in range(st.session_state.rows):
            if st.session_state.get(f"p{i}"):
                pdf.add_data(st.session_state[f"p{i}"], f"{st.session_state[f'm{i}']} m2")

        pdf.section_header("Synthèse Financière")
        pdf.add_data("Total TTC", f"{total:.2f} Euros")

        buf = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER LE PDF", buf, "Rapport_FD.pdf", "application/pdf")
    except Exception as e:
        st.error(f"Erreur lors de la génération : {e}")