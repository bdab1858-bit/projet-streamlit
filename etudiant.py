import streamlit as st
import pandas as pd
from bd import get_connection

# ================== ROLE CHECK ==================
if st.session_state.get("user_role") != "etudiant":
    st.error("Accès refusé. Cette page est réservée aux étudiants.")
    st.stop()

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Étudiant | Emploi du temps",
    page_icon="🎓",
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
    border-left: 6px solid #4CAF50;
    margin-bottom: 20px;
}

.header {
    background: linear-gradient(90deg, #4CAF50, #66BB6A);
    padding: 28px;
    border-radius: 20px;
    color: white;
    margin-bottom: 30px;
}

.info-box {
    background-color: #E8F5E9;
    padding: 16px;
    border-radius: 10px;
    border-left: 4px solid #4CAF50;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
etudiant_id = st.session_state.get("user_id")

st.markdown("""
<div class="header">
    <h1>🎓 Mon Emploi du Temps</h1>
    <p>Consultation de vos examens programmés</p>
</div>
""", unsafe_allow_html=True)

# ================== DATA ==================
try:
    conn = get_connection()
    cur = conn.cursor()

    # Student info
    cur.execute("""
        SELECT nom, prenom
        FROM etudiant
        WHERE id_etud = %s
    """, (etudiant_id,))
    etud = cur.fetchone()

    if etud:
        nom, prenom = etud
        st.markdown(f"""
        <div class="info-box">
            <b>Étudiant :</b> {prenom} {nom}
        </div>
        """, unsafe_allow_html=True)

    # ================== EXAMS ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Mes Examens")

    cur.execute("""
        SELECT
            m.nom,
            s.nom,
            c.date_exam,
            c.heure_debut,
            c.heure_fin,
            p.nom
        FROM examen e
        JOIN module m ON e.id_module = m.id_module
        JOIN salle s ON e.id_salle = s.id_salle
        JOIN creneau c ON e.id_creneau = c.id_creneau
        JOIN professeur p ON e.id_prof = p.id_prof
        JOIN inscription i ON i.id_module = e.id_module
        WHERE i.id_etud = %s
        ORDER BY c.date_exam, c.heure_debut
    """, (etudiant_id,))

    exams = cur.fetchall()

    if exams:
        df = pd.DataFrame(
            exams,
            columns=["Module", "Salle", "Date", "Début", "Fin", "Professeur"]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucun examen programmé.")

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
st.caption("Projet universitaire — Interface Étudiant")
