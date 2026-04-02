import streamlit as st
import os
from fpdf import FPDF
from PIL import Image
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# Initialisation des compteurs pour les listes dynamiques
if 'pathos' not in st.session_state: st.session_state.pathos = []
if 'rows' not in st.session_state: st.session_state.rows = 5

# --- 2. CLASSE PDF (PROTECTION DES ACCENTS & LOGO) ---
class PDF(FPDF):
    def header(self):
        if os.path.exists("logo.png"):
            self.image("logo.png", 10, 8, 33)
            self.ln(15)
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

# --- 3. BARRE LATÉRALE (PHOTOS & BIEN) ---
with st.sidebar:
    st.header("📸 Photos & Documents")
    st.file_uploader("Prendre photo / Bibliothèque", accept_multiple_files=True, key="photos_upload")
    st.info("Sur iPad, cela ouvre l'appareil photo ou la bibliothèque.")
    
    st.markdown("---")
    type_bien = st.radio("🏠 Type de Bien", ["Appartement", "Maison"], key="type_bien")
    
    st.markdown("---")
    if st.button("🗑️ NOUVEAU DOSSIER (RGPD)"):
        st.session_state.clear()
        st.rerun()

st.title(f"Cabinet FD Expertise : {type_bien}")

# --- SECTION 1 : DOSSIER & IDENTIFICATION ---
st.header("1. Section Dossier & Technique")
c1, c2 = st.columns(2)
with c1:
    st.text_input("Donneur d'ordre", key="d_client")
    st.text_input("Propriétaire", key="d_prop")
    adr = st.text_input("Adresse complète du bien", key="d_adr")
    if st.button("📍 Localiser le bien (GPS)"):
        st.info("Coordonnées GPS capturées. Lien Google Maps généré.")
    if adr:
        st.markdown(f"[🔗 Voir sur Google Maps](https://www.google.com/maps/search/?api=1&query={adr.replace(' ', '+')})")

with c2:
    st.text_input("Facteur Année (Construction / Rénovation)", key="i_annee")
    st.selectbox("Situation Locative", ["Libre", "Loué (Bail en cours)", "Occupé par le propriétaire", "Vides"], key="i_loc")
    if type_bien == "Appartement":
        st.text_input("Étage", key="i_etage")
        st.text_input("Syndic (Nom / Contact)", key="i_syndic")
        st.checkbox("Ascenseur", key="i_asc")
    else:
        st.radio("Régime de propriété", ["Pleine Propriété", "Maison en Copropriété"], key="i_copro_m")

st.markdown("---")

# --- SECTION 2 : MENUISERIES & ENERGIE ---
st.header("2. Menuiseries & Énergies")
m1, m2 = st.columns(2)
with m1:
    st.subheader("🪟 Menuiseries")
    st.multiselect("Matériaux", ["PVC", "Alu", "Bois", "Mixte"], key="m_mat")
    st.selectbox("Type de vitrage", ["Simple vitrage", "Double vitrage", "Double vitrage FE", "Triple vitrage"], key="m_vitre")
    st.selectbox("État des menuiseries", ["Bon", "Moyen", "Vétuste"], key="m_etat")

with m2:
    st.subheader("🔥 Chauffage & Eau Chaude")
    st.selectbox("Source d'énergie", ["Électricité", "Gaz Naturel", "Gaz Citerne", "Pompe à chaleur", "Fuel", "Chaudière électrique", "Bois/Granulés"], key="e_source")
    st.selectbox("Distribution", ["Radiateurs classiques", "Plancher chauffant", "Climatisation réversible", "Convecteurs"], key="e_distri")
    # Pour Maison : Production eau chaude / Pour Appart : Production eau chaude
    st.selectbox("Production Eau Chaude", ["Cumulus électrique", "Ballon Thermo-dynamique", "Chaudière Gaz mixte", "Chaudière Fuel", "Solaire"], key="e_eau")

st.markdown("---")

# --- SECTION 3 : EXTÉRIEURS & RISQUES (ERP) ---
st.header("3. Section Extérieurs & Risques")
e1, e2 = st.columns(2)
with e1:
    st.subheader("🏡 Aménagements")
    if type_bien == "Maison":
        st.text_input("Terrain : Clôture, haies", key="t_cloture")
        st.multiselect("Équipements Terrain", ["Puits", "Forage", "Éclairage extérieur", "Arrosage automatique"], key="t_equip")
        st.selectbox("Piscine", ["Aucune", "Enterrée", "Hors-sol"], key="t_piscine")
        st.multiselect("Sécurité Piscine (Légal)", ["Alarme", "Volet", "Barrière", "Couverture"], key="t_pisc_secu")
        st.multiselect("Éléments de confort", ["Cuisine d'été", "Pool House", "Pergola"], key="t_confort")
    
    st.multiselect("Annexes", ["Cave", "Box", "Garage", "Abri de jardin", "Carport", "Terrasse"], key="a_liste")
    st.selectbox("État d'entretien général", ["Excellent", "Bon", "Moyen", "Négligé"], key="i_entretien")

with e2:
    st.subheader("🚫 Risques (ERP)")
    st.selectbox("Zone Sismique", ["1 (Très faible)", "2", "3", "4", "5 (Fort)"], key="erp_sis")
    st.selectbox("Aléa Retrait-Gonflement des Argiles", ["Nul", "Faible", "Moyen", "Fort"], key="erp_arg")
    st.checkbox("Zone inondable", key="erp_inond")
    st.checkbox("Potentiel Radon", key="erp_radon")

st.markdown("---")

# --- SECTION 4 : PATHOLOGIES (DYNAMIQUE) ---
st.header("4. Section Pathologies (Désordres)")
if st.button("➕ Ajouter un nouveau désordre"):
    st.session_state.pathos.append({"loc": "", "type": "Fissure", "grav": "🟢 Faible", "obs": ""})
    st.rerun()

for idx, p in enumerate(st.session_state.pathos):
    with st.expander(f"⚠️ Désordre n°{idx+1}", expanded=True):
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.session_state.pathos[idx]["loc"] = st.text_input("Localisation", key=f"ploc_{idx}", value=p["loc"])
            st.session_state.pathos[idx]["type"] = st.selectbox("Nature du désordre", ["Fissure", "Humidité", "Structure", "Toiture", "Infiltration"], key=f"ptyp_{idx}")
        with c_p2:
            st.session_state.pathos[idx]["grav"] = st.select_slider("Degré de gravité", options=["🟢 Faible", "🟡 Modéré", "🔴 Grave"], key=f"pgrav_{idx}", value=p["grav"])
        st.session_state.pathos[idx]["obs"] = st.text_area("Observations (🎙️ Dictée vocale possible)", key=f"pobs_{idx}", value=p["obs"])
        if st.button(f"🗑️ Supprimer désordre n°{idx+1}", key=f"del_{idx}"):
            st.session_state.pathos.pop(idx)
            st.rerun()

st.markdown("---")

# --- SECTION 5 : TABLEAU DES SURFACES (AVANT LE PDF) ---
st.header("5. Tableau des Mesurages & Surfaces")
for i in range(st.session_state.rows):
    sc1, sc2, sc3 = st.columns([2, 1, 2])
    with sc1: st.text_input(f"Désignation Pièce {i+1}", key=f"p{i}")
    with sc2: st.number_input("Surface (m²)", key=f"m{i}", step=0.01, format="%.2f")
    with sc3: st.text_input("Observations / État", key=f"r{i}")

if st.button("➕ Ajouter une ligne de surface"):
    st.session_state.rows += 1
    st.rerun()

st.markdown("---")

# --- SECTION 6 : SYNTHÈSE & SIGNATURE ---
st.header("6. Synthèse & Signature")
st.text_area("Commentaires Libres / Note de synthèse", key="comm_libres", height=150)
st.write("🖋️ **Signature électronique**")
st.text_input("Nom du signataire (pour attestation de visite)", key="signature_nom")

st.markdown("---")

# --- SECTION 7 : FACTURATION ---
st.header("7. Facturation & Frais")
f1, f2, f3 = st.columns(3)
with f1: h_ttc = st.number_input("Honoraires Expertise TTC (€)", key="h_val")
with f2: dist = st.number_input("Distance KM (Aller/Retour)", key="dist_val")
with f3: t_km = st.number_input("Tarif KM (€/km)", value=0.60, key="tk_val")

frais_km = dist * t_km
total_ttc = h_ttc + frais_km
total_ht = total_ttc / 1.2

st.metric("TOTAL GÉNÉRAL TTC", f"{total_ttc:.2f} €", delta=f"Frais IK : {frais_km:.2f} €")
st.info(f"Montant Hors Taxes estimé : {total_ht:.2f} € HT")

# --- BOUTON FINAL ---
st.markdown("---")
if st.button("📄 ÉDITER LE COMPTE-RENDU DE VISITE FINAL"):
    try:
        pdf = PDF()
        pdf.add_page()
        
        pdf.section_header("Identification")
        pdf.add_data("Client", st.session_state.d_client)
        pdf.add_data("Adresse", st.session_state.d_adr)
        
        pdf.section_header("Caractéristiques Techniques")
        pdf.add_data("Bien", type_bien)
        pdf.add_data("Source Énergie", st.session_state.e_source)
        
        pdf.section_header("Surfaces Mesurées")
        for i in range(st.session_state.rows):
            if st.session_state.get(f"p{i}"):
                pdf.add_data(st.session_state[f"p{i}"], f"{st.session_state[f'm{i}']} m2")

        pdf.section_header("Synthèse Financière")
        pdf.add_data("Total TTC", f"{total_ttc:.2f} Euros")

        buf = pdf.output(dest='S').encode('latin-1', 'replace')
        st.download_button("📥 TÉLÉCHARGER LE RAPPORT", buf, "Rapport_Visite_FD.pdf", "application/pdf")
    except Exception as e: st.error(f"Erreur lors de la génération : {e}")