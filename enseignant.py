
 import streamlit as st
import pandas as pd
from bd import get_connection

# ================== ROLE CHECK ==================
if st.session_state.get("user_role") != "enseignant":
    st.error("Accès refusé. Seuls les enseignants peuvent accéder à cette page.")
    st.stop()

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Enseignant | Examens",
    page_icon="👨‍🏫",
    layout="wide"
)

# ================== HIDE SIDEBAR ==================
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

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

.info-box {
    background-color: #E3F2FD;
    padding: 16px;
    border-radius: 10px;
    border-left: 4px solid #2196F3;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
prof_id = st.session_state.get("user_id")

st.markdown("""
<div class="header">
    <h1>👨‍🏫 Espace Enseignant</h1>
    <p>Gestion de vos examens et surveillances</p>
</div>
""", unsafe_allow_html=True)

# ================== DATABASE ==================
try:
    conn = get_connection()
    cur = conn.cursor()

    # ---------- Enseignant + Département + Chef ----------
    cur.execute("""
        SELECT 
            p.nom AS prof_nom,
            d.nom AS dept_nom,
            cd.nom AS chef_nom
        FROM professeur p
        JOIN departement d ON p.id_dept = d.id_dept
        LEFT JOIN professeur cd 
            ON cd.id_dept = d.id_dept AND cd.role = 'chef_dept'
        WHERE p.id_prof = %s
    """, (prof_id,))

    info = cur.fetchone()

    if info:
        prof_nom, dept_nom, chef_nom = info

        st.markdown(f"""
        <div class="info-box">
            <b>Enseignant :</b> {prof_nom}<br>
            <b>Département :</b> {dept_nom}<br>
            <b>Chef de département :</b> {chef_nom if chef_nom else "Non défini"}
        </div>
        """, unsafe_allow_html=True)

    # ================== KPI ==================
    cur.execute("SELECT COUNT(*) FROM examen WHERE id_prof = %s", (prof_id,))
    total_exams = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM surveillance WHERE id_prof = %s", (prof_id,))
    total_surv = cur.fetchone()[0]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>📝 Examens</h3>
            <div class="kpi">{total_exams}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="card">
            <h3>👁️ Surveillances</h3>
            <div class="kpi">{total_surv}</div>
        </div>
        """, unsafe_allow_html=True)

    # ================== MES EXAMENS ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Mes Examens")

    cur.execute("""
        SELECT 
            m.nom,
            s.nom,
            c.date_exam,
            c.heure_debut,
            c.heure_fin
        FROM examen e
        JOIN module m ON e.id_module = m.id_module
        JOIN salle s ON e.id_salle = s.id_salle
        JOIN creneau c ON e.id_creneau = c.id_creneau
        WHERE e.id_prof = %s
        ORDER BY c.date_exam, c.heure_debut
    """, (prof_id,))

    exams = cur.fetchall()

    if exams:
        df = pd.DataFrame(
            exams,
            columns=["Module", "Salle", "Date", "Heure début", "Heure fin"]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucun examen assigné.")

    st.markdown('</div>', unsafe_allow_html=True)

    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Erreur : {e}")

# ================== LOGOUT ==================
st.divider()

if st.button("🚪 Se déconnecter"):
    st.session_state.clear()
    st.switch_page("pages/login.py")

# ================== FOOTER ==================
st.caption("Projet universitaire — Interface Enseignant"
