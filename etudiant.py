import streamlit as st
import pandas as pd
from bd import get_connection

# Role-based access control - allow students and teachers
if st.session_state.get('user_role') not in ['etudiant', 'enseignant']:
    st.error("Accès refusé. Seuls les étudiants et enseignants peuvent accéder à cette page.")
    st.stop()

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Étudiant | Emploi du temps",
    page_icon="🎓",
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
etudiant_id = st.session_state.get('user_id')
st.markdown(f"""
<div class="header">
    <h1>🎓 Mon Emploi du Temps</h1>
    <p>Consultation de vos examens programmés</p>
</div>
""", unsafe_allow_html=True)

try:
    conn = get_connection()
    cur = conn.cursor()
    
    # Get student info
    cur.execute("SELECT nom, prenom, id_form FROM etudiant WHERE id_etud = %s", (etudiant_id,))
    etud_info = cur.fetchone()
    
    if etud_info:
        nom, prenom, id_form = etud_info
        st.markdown(f"""
        <div class="info-box">
            <b>Étudiant:</b> {prenom} {nom}
        </div>
        """, unsafe_allow_html=True)
    
    # ================== MY EXAMS ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📋 Mes Examens")
    
    cur.execute("""
        SELECT 
            e.id_examen,
            m.nom AS module_name,
            s.nom AS salle_name,
            c.date_exam,
            c.heure_debut,
            c.heure_fin,
            p.nom || ' ' || p.prenom AS professeur
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
        exam_df = pd.DataFrame(exams, columns=['ID Exam', 'Module', 'Salle', 'Date', 'Heure début', 'Heure fin', 'Professeur'])
        # Hide ID column
        exam_df_display = exam_df.drop('ID Exam', axis=1)
        st.dataframe(exam_df_display, use_container_width=True)
    else:
        st.info("Aucun examen programmé pour le moment.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ================== STATISTICS ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📊 Statistiques")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_exams = len(exams) if exams else 0
        st.metric("📝 Total Examens", num_exams)
    
    with col2:
        if exams:
            dates = [e[3] for e in exams]
            num_days = len(set(dates))
            st.metric("📅 Jours d'examens", num_days)
        else:
            st.metric("📅 Jours d'examens", 0)
    
    with col3:
        if exams:
            num_modules = len(set([e[1] for e in exams]))
            st.metric("📚 Modules", num_modules)
        else:
            st.metric("📚 Modules", 0)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Erreur lors du chargement des données: {e}")

# ================== FOOTER ==================
st.caption("Projet universitaire — Interface Étudiant")