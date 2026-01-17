import streamlit as st
import pandas as pd

from algorithme import generate_exam_schedule, persist_schedule_to_db
from db_queries import (
    count_examens,
    count_salles,
    count_conflicts,
    count_salles_utilisees,
    exams_per_day
)

# ================== PAGE CONFIG (TOUJOURS EN PREMIER) ==================
st.set_page_config(
    page_title="Admin | Optimisation Examens",
    page_icon="🛠",
    layout="wide"
)

# ================== ROLE CHECK ==================
if st.session_state.get("user_role") != "admin":
    st.error("⛔ Accès refusé. Seuls les administrateurs peuvent accéder à cette page.")
    st.stop()

# ================== HIDE SIDEBAR ==================
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ================== STYLE ==================
st.markdown("""
<style>
.stApp { background-color: #F1F4F9; font-family: 'Segoe UI', sans-serif; }

.header {
    background: linear-gradient(90deg, #5B9DFF, #6EC6FF);
    padding: 30px;
    border-radius: 20px;
    color: white;
    margin-bottom: 30px;
}

.card {
    background-color: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.1);
    margin-bottom: 25px;
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
    <h1>🛠 Administrateur des Examens</h1>
    <p>Planification et génération automatique des emplois du temps</p>
</div>
""", unsafe_allow_html=True)

# ================== KPI ==================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card">
        <h3>📘 Examens</h3>
        <div class="kpi">{count_examens()}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <h3>⚠️ Conflits</h3>
        <div class="kpi">{count_conflicts()}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    used = count_salles_utilisees()
    total = count_salles()
    st.markdown(f"""
    <div class="card">
        <h3>🏫 Salles</h3>
        <div class="kpi">{used} / {total}</div>
    </div>
    """, unsafe_allow_html=True)

# ================== CONFIGURATION ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("⚙️ Paramètres")

periode = st.selectbox("📅 Période", ["Semestre 1", "Semestre 2"])
duree = st.selectbox("⏱ Durée", ["1h", "1h30", "2h"])

st.markdown('</div>', unsafe_allow_html=True)

# ================== GENERATION ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🚀 Génération automatique")

auto_save = st.checkbox("💾 Enregistrer automatiquement en base", value=True)

if st.button("⚙️ Générer l’emploi du temps"):
    try:
        planning = generate_exam_schedule()
        df = pd.DataFrame(planning)

        if df.empty:
            st.warning("Aucun examen généré")
        else:
            st.success("Emploi du temps généré avec succès")

            st.dataframe(df[["module", "salle", "date", "heure"]], use_container_width=True)

            if auto_save:
                persist_schedule_to_db(planning)
                st.success("Emploi du temps enregistré en base")

    except Exception as e:
        st.error(f"Erreur : {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ================== STATS ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📊 Examens par jour")

rows = exams_per_day()
if rows:
    df = pd.DataFrame(rows, columns=["Date", "Examens"])
    st.bar_chart(df.set_index("Date"))
else:
    st.info("Aucune donnée")

st.markdown('</div>', unsafe_allow_html=True)

# ================== LOGOUT ==================
if st.button("🚪 Se déconnecter"):
    st.session_state.clear()
    st.switch_page("pages/login.py")

# ================== FOOTER ==================
st.caption("Projet universitaire — Génération automatique des examens")
