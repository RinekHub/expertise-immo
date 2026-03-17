import streamlit as st
import os

# 1. Configuration pro
st.set_page_config(page_title="Cabinet FD Expertise", layout="wide")

# 2. BARRE LATÉRALE (Le menu à gauche)
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.title("⚙️ Paramètres")
    secteur = st.radio("Secteur d'intervention", ["📍 Nouvelle-Aquitaine", "📍 Paris / IDF"])
    date_visite = st.date_input("Date de la visite")
    st.info("Utilisez ce menu pour configurer le dossier en cours.")

# 3. CORPS DE LA PAGE (Le formulaire principal)
st.title("🏛️ Cabinet FD Expertise")
st.markdown(f"**Dossier en cours :** {secteur} | Visite du {date_visite}")
st.divider()

with st.form("expertise_form"):
    st.subheader("📝 Détails de l'Expertise")
    
    col1, col2 = st.columns(2)
    with col1:
        client = st.text_input("Nom du Client / Référence")
        type_mission = st.selectbox("Type de Mission", 
                                  ["Valeur Vénale Classique", "Viager", "Préjudice Visuel", "Succession"])
    with col2:
        adresse = st.text_input("Adresse du bien")
        surface = st.number_input("Surface (m²)", min_value=0)

    # --- RUBRIQUES DYNAMIQUES ---
    if type_mission == "Valeur Vénale Classique":
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            etat = st.selectbox("État général", ["Excellent", "Bon", "Moyen", "À rénover"])
        with c2:
            dpe = st.selectbox("DPE", ["A", "B", "C", "D", "E", "F", "G"], index=3)

    elif type_mission == "Viager":
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
            age = st.number_input("Âge du crédirentier", 50, 110, 75)
        with c2:
            bouquet = st.number_input("Bouquet souhaité (€)", min_value=0)

    st.divider()
    notes = st.text_area("Observations de terrain", height=150)
    
    submit = st.form_submit_button("💾 Enregistrer les notes")

if submit:
    st.success(f"Dossier {client} mis à jour !")