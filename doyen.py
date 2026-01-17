import streamlit as st
import pandas as pd
from bd import get_connection

# 🚫 Hide sidebar
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

# Role-based access control
if st.session_state.get('user_role') != 'doyen':
    st.error("Accès refusé.")
    st.stop()

st.set_page_config(
    page_title="Doyen",
    page_icon="📊",
    layout="wide"
)

# 🔹 Récupérer le nom du doyen
conn = get_connection()
cur = conn.cursor()

cur.execute(
    "SELECT nom FROM professeur WHERE id_prof = %s",
    (st.session_state.get("user_id"),)
)
row = cur.fetchone()
cur.close()
conn.close()

doyen_nom = row[0] if row else "Doyen"

# ================== HEADER ==================
st.markdown(f"""
<div style="
background: linear-gradient(90deg, #5B9DFF, #6EC6FF);
padding: 30px;
border-radius: 20px;
color: white;
margin-bottom: 30px;">
    <h1>📊 Doyen / Vice‑Doyen</h1>
    <p><b>{doyen_nom}</b></p>
</div>
""", unsafe_allow_html=True)


# ================== KPI ==================
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

# ================== DATA ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📊 Examens par département")

df = pd.DataFrame({
    "Département": ["Informatique", "Mathématiques", "Physique", "Chimie"],
    "Examens": [60, 55, 45, 40]
})

st.bar_chart(df.set_index("Département"))
st.markdown('</div>', unsafe_allow_html=True)

# ================== ACTIONS ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("✅ Décisions")

c1, c2 = st.columns(2)
with c1:
    st.button("✔️ Valider le planning global")
with c2:
    st.button("📄 Exporter le planning (PDF)")

st.info("Les actions seront effectives après connexion à la base de données.")
st.markdown('</div>', unsafe_allow_html=True)
if st.button("🚪 Se déconnecter"):
    # Clear session
    st.session_state.user_role = None
    st.session_state.user_id = None

    # Optional: clear all session state
    st.session_state.clear()

    # Redirect to login page
    st.switch_page("pages/login.py")
# ================== FOOTER ==================
st.caption("Projet universitaire — Interface décisionnelle du Doyen")
