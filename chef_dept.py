import streamlit as st
import pandas as pd
from bd import get_connection

# ================== PAGE CONFIG (TOUJOURS EN PREMIER) ==================
st.set_page_config(
    page_title="Chef de département",
    page_icon="🏫",
    layout="wide"
)

# ================== HIDE SIDEBAR ==================
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ================== ROLE CHECK ==================
if st.session_state.get('user_role') != 'chef_dept':
    st.error("Accès refusé. Seuls les chefs de département peuvent accéder à cette page.")
    st.stop()

# ================== GET CHEF INFO ==================
chef_id = st.session_state.get("user_id")

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT nom, specialite
        FROM professeur
        WHERE id_prof = %s
    """, (chef_id,))
    chef = cur.fetchone()

    if chef:
        nom_chef, specialite = chef
    else:
        nom_chef, specialite = "Inconnu", "Inconnue"

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Erreur base de données : {e}")
    st.stop()

# ================== STYLE ==================
st.markdown("""
<style>
.stApp {
    background-color: #F1F4F9;
    font-family: 'Segoe UI', sans-serif;
}

.card {
    background-color: white;
    padding: 28px;
    border-radius: 16px;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.08);
    border-left: 6px solid #5B9DFF;
    margin-bottom: 20px;
}

.header {
    background: linear-gradient(90deg, #5B9DFF, #6EC6FF);
    padding: 28px;
    border-radius: 20px;
    color: white;
    margin-bottom: 30px;
}

.kpi {
    font-size: 34px;
    font-weight: bold;
    color: #5B9DFF;
}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown(f"""
<div class="header">
    <h1>🏫 Chef de département</h1>
    <p><b>{nom_chef}</b> — {specialite}</p>
</div>
""", unsafe_allow_html=True)

# ================== KPI ==================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <h3>📘 Modules</h3>
        <div class="kpi">12</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3>📝 Examens</h3>
        <div class="kpi">45</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <h3>⚠️ Conflits</h3>
        <div class="kpi">3</div>
    </div>
    """, unsafe_allow_html=True)

# ================== EXAMS LIST ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📋 Examens du département")

df = pd.DataFrame({
    "Module": ["Programmation", "Bases de données", "Réseaux", "IA"],
    "Date": ["12/01/2026", "14/01/2026", "16/01/2026", "18/01/2026"],
    "Salle": ["A1", "B2", "C3", "D1"],
    "Statut": ["En attente", "En attente", "Validé", "En attente"]
})

st.dataframe(df, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ================== VALIDATION ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("✅ Validation")

col1, col2 = st.columns(2)

with col1:
    st.button("✔️ Valider tous les examens")

with col2:
    st.button("⚠️ Signaler un conflit")

st.info("Les validations seront enregistrées après connexion à la base de données.")
st.markdown('</div>', unsafe_allow_html=True)
st.divider()

if st.button("🚪 Se déconnecter"):
    # Clear session
    st.session_state.user_role = None
    st.session_state.user_id = None

    # Optional: clear all session state
    st.session_state.clear()

    # Redirect to login page
    st.switch_page("pages/login.py")

# ================== FOOTER ==================
st.caption("Projet universitaire — Interface Chef de département")
