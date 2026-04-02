import streamlit as st
import os
import json
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURATION & DOSSIER SERVEUR ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")
SAVE_DIR = "sauvegardes"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# --- 2. LOGIQUE DE SAUVEGARDE (ANTI-PERTE) ---
def sauver_sur_serveur():
    """Enregistre tout le contenu du formulaire dans un fichier sur le serveur"""
    # On capture tout ce qui est dans la session (les inputs avec des 'key')
    data = {k: v for k, v in st.session_state.items() if not k.startswith('FormSubmitter')}
    with open(os.path.join(SAVE_DIR, "sauvegarde_en_cours.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def charger_depuis_serveur():
    """Récupère les données au démarrage de l'app"""
    path = os.path.join(SAVE_DIR, "sauvegarde_en_cours.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                st.session_state[k] = v

# --- 3. INITIALISATION ---
if 'init_done' not in st.session_state:
    charger_depuis_serveur()
    st.session_state['init_done'] = True

if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 5

# --- 4. CLASSE PDF ---
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

# --- 5. BARRE LATÉRALE ---
with st.sidebar:
    if os.path.exists("logo.png"): st.image("logo.png", width=150)
    st.markdown("---")
    # Choix du bien avec sauvegarde immédiate
    type_bien = st.radio("🏠 Type de Bien", ["Appartement", "Maison"], key="type_bien", on_change=sauver_sur_serveur)
    st.markdown("---")
    menu = st.radio("📍 Navigation", ["📝 1. Expertise Technique", "💰 2. Facturation & PDF"])
    st.markdown("---")
    
    # BOUTON RGPD : Efface la session ET le fichier serveur
    if st.button("🗑️ EFFACER TOUTES LES DONNÉES (RGPD)", help="Supprime le fichier du serveur et vide l'app"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        if os.path.exists(os.path.join(SAVE_DIR, "sauvegarde_en_cours.json")):
            os.remove(os.path.join(SAVE_DIR, "sauvegarde_en_cours.json"))
        st.rerun()

# --- PAGE 1 : EXPERTISE TECHNIQUE (CONDENSÉE) ---
if menu == "📝 1. Expertise Technique":
    st.title(f"📋 Expertise : {st.session_state.get('type_bien', 'Appartement')}")
    
    # A. DOSSIER & IMMEUBLE
    st.subheader("1. Dossier & Immeuble")
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Donneur d'ordre", key="d_client", on_change=sauver_sur_serveur)
        st.text_input("Adresse du bien", key="d_adr", on_change=sauver_sur_serveur)
        st.text_input("Propriétaire", key="d_prop", on_change=sauver_sur_serveur)
    with c2:
        st.text_input("Année de construction", key="i_annee", on_change=sauver_sur_serveur)
        st.selectbox("Situation locative", ["Libre", "Occupé", "Loué", "Vides"], key="i_loc", on_change=sauver_sur_serveur)
        if st.session_state.get('type_bien') == "Appartement":
            st.text_input("Étage", key="i_etage", on_change=sauver_sur_serveur)
            st.text_input("Syndic", key="i_syndic", on_change=sauver_sur_serveur)
        else:
            st.text_input("Surface Terrain (m²)", key="i_terrain", on_change=sauver_sur_serveur)
            st.text_input("Type de toiture", key="i_toit", on_change=sauver_sur_serveur)

    # B. SURFACES & ANNEXES
    st.markdown("---")
    st.subheader("2. Surfaces & Annexes")
    for i in range(st.session_state.rows):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1: st.text_input(f"Pièce {i+1}", key=f"p{i}", on_change=sauver_sur_serveur)
        with sc2: st.number_input("m²", key=f"m{i}", step=0.01, format="%.2f", on_change=sauver_sur_serveur)
        with sc3: st.text_input("État/Observations", key=f"r{i}", on_change=sauver_sur_serveur)
    
    if st.button("➕ Ajouter une pièce"):
        st.session_state.rows += 1
        sauver_sur_serveur()
        st.rerun()

    st.multiselect("Annexes présentes", ["Garage", "Cave", "Parking", "Balcon", "Terrasse", "Grenier"], key="a_liste", on_change=sauver_sur_serveur)

    # C. EXTÉRIEURS & RISQUES
    st.markdown("---")
    st.subheader("3. Extérieurs & Risques")
    ec1, ec2 = st.columns(2)
    with ec1:
        if st.session_state.get('type_bien') == "Maison":
            st.multiselect("Équipements", ["Jardin", "Clôture", "Portail élec", "Piscine"], key="e_amen", on_change=sauver_sur_serveur)
        st.text_area("Observations terrain / Parties Communes", key="e_comm", on_change=sauver_sur_serveur)
    with ec2:
        st.selectbox("Zone Sismique", ["1", "2", "3", "4", "5"], key="e_sis", on_change=sauver_sur_serveur)
        st.checkbox("Zone inondable", key="e_inond", on_change=sauver_sur_serveur)

    # D. PATHOLOGIES
    st.markdown("---")
    st.subheader("4. Pathologies (Désordres)")
    if st.button("➕ Ajouter un désordre"):
        st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢", "obs": ""})
        sauver_sur_serveur()
        st.rerun()

    for idx, p in enumerate(st.session_state.pathos):
        with st.expander(f"Désordre n°{idx+1}", expanded=True):
            st.session_state.pathos[idx]["loc"] = st.text_input("Lieu", key=f"ploc_{idx}", value=p["loc"], on_change=sauver_sur_serveur)
            st.session_state.pathos[idx]["type"] = st.selectbox("Type", ["Fissure", "Humidité", "Structure", "Infiltration"], key=f"ptyp_{idx}", index=["Fissure", "Humidité", "Structure", "Infiltration"].index(p["type"]), on_change=sauver_sur_serveur)
            st.session_state.pathos[idx]["obs"] = st.text_area("Obs.", key=f"pobs_{idx}", value=p["obs"], on_change=sauver_sur_serveur)
            if st.button(f"🗑️ Supprimer n°{idx+1}", key=f"del_{idx}"):
                st.session_state.pathos.pop(idx)
                sauver_sur_serveur()
                st.rerun()

# --- PAGE 2 : FACTURATION & PDF ---
elif menu == "💰 2. Facturation & PDF":
    st.title("💰 Facturation & PDF")
    
    f1, f2, f3 = st.columns(3)
    with f1: h_ttc = st.number_input("Honoraires TTC (€)", key="h_val", on_change=sauver_sur_serveur)
    with f2: dist = st.number_input("Distance KM (A/R)", key="dist_val", on_change=sauver_sur_serveur)
    with f3: t_km = st.number_input("Tarif KM (€)", value=0.60, key="tk_val", on_change=sauver_sur_serveur)
    
    total = h_ttc + (dist * t_km)
    st.metric("TOTAL TTC", f"{total:.2f} €")
    st.session_state['final_total'] = total

    st.markdown("---")
    if st.button("📄 GÉNÉRER LE RAPPORT PDF"):
        sauver_sur_serveur()
        try:
            pdf = PDF()
            pdf.add_page()
            pdf.section_header(f"IDENTIFICATION DU BIEN ({st.session_state.type_bien.upper()})")
            pdf.add_data("Client", st.session_state.get('d_client', ''))
            pdf.add_data("Adresse", st.session_state.get('d_adr', ''))
            
            pdf.section_header("SURFACES")
            for i in range(st.session_state.rows):
                p_name = st.session_state.get(f"p{i}")
                if p_name:
                    pdf.add_data(p_name, f"{st.session_state.get(f'm{i}', 0.0)} m2")

            pdf.section_header("FINANCES")
            pdf.add_data("TOTAL TTC", f"{st.session_state.get('final_total', 0.0):.2f} Euros")

            res = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("📥 TÉLÉCHARGER LE PDF", res, "Expertise_FD.pdf", "application/pdf")
        except Exception as e: st.error(f"Erreur PDF : {e}")