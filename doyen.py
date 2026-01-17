import streamlit as st
import pandas as pd

# Role-based access control
if st.session_state.get('user_role') != 'doyen':
    st.error("Accès refusé. Seuls les doyens peuvent accéder à cette page.")
    st.stop()

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Doyen | Examens",
    page_icon="📊",
    layout="wide"
)

# ================== STYLE ==================
st.markdown("""
<style>
.stApp {
    background-color: #F1F4F9;
    font-family: 'Segoe UI', sans-serif;
}

.card {
    background-color: white;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0px 10px 25px rgba(0,0,0,0.08);
    border-left: 6px solid #5B9DFF;
    margin-bottom: 20px;
}

.header {
    background: linear-gradient(90deg, #5B9DFF, #6EC6FF);
    padding: 30px;
    border-radius: 20px;
    color: white;
    margin-bottom: 30px;
}

.kpi {
    font-size: 36px;
    font-weight: bold;
    color: #5B9DFF;
}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("""
<div class="header">
    <h1>📊 Doyen / Vice‑Doyen</h1>
    <p>Vue globale et supervision des emplois du temps d’examens</p>
</div>
""", unsafe_allow_html=True)

# ================== KPI CARDS ==================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <h3>📘 Examens</h3>
        <div class="kpi">240</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3>⚠️ Conflits</h3>
        <div class="kpi">12</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <h3>🏫 Salles</h3>
        <div class="kpi">35</div>
    </div>
    """, unsafe_allow_html=True)

# ================== DATA VISUALIZATION ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📊 Examens par département")

df = pd.DataFrame({
    "Département": ["Informatique", "Mathématiques", "Physique", "Chimie"],
    "Examens": [60, 55, 45, 40]
})

st.bar_chart(df.set_index("Département"))
st.markdown('</div>', unsafe_allow_html=True)

# ================== DECISION ACTIONS ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("✅ Décisions")

col1, col2 = st.columns(2)

with col1:
    st.button("✔️ Valider le planning global")

with col2:
    st.button("📄 Exporter le planning (PDF)")

st.info("Les actions seront effectives après connexion à la base de données.")
st.markdown('</div>', unsafe_allow_html=True)

# ================== FOOTER ==================
st.caption("Projet universitaire — Tableau de bord décisionnel du Doyen")