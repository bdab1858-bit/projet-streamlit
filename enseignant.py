import streamlit as st
import pandas as pd
from bd import get_connection

# Role-based access control
if st.session_state.get('user_role') != 'enseignant':
    st.error("Accès refusé. Seuls les enseignants peuvent accéder à cette page.")
    st.stop()

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="Enseignant | Examens",
    page_icon="👨‍🏫",
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
prof_id = st.session_state.get('user_id')
st.markdown(f"""
<div class="header">
    <h1>👨‍🏫 Espace Enseignant</h1>
    <p>Gestion de vos examens et surveillances (ID: {prof_id})</p>
</div>
""", unsafe_allow_html=True)

# Get professor info
try:
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT nom, prenom, id_dept FROM professeur WHERE id_prof = %s", (prof_id,))
    prof_info = cur.fetchone()
    
    if prof_info:
        nom, prenom, id_dept = prof_info
        st.markdown(f"""
        <div class="info-box">
            <b>Enseignant:</b> {prenom} {nom} | <b>Département ID:</b> {id_dept}
        </div>
        """, unsafe_allow_html=True)
    
    # ================== KPI ==================
    # Count exams for this professor
    cur.execute("SELECT COUNT(*) FROM examen WHERE id_prof = %s", (prof_id,))
    total_exams = cur.fetchone()[0]
    
    # Count modules taught by this professor
    cur.execute("""
        SELECT COUNT(DISTINCT m.id_module) 
        FROM module m
        WHERE m.id_form IN (SELECT id_form FROM formation WHERE id_dept = %s)
    """, (id_dept,))
    total_modules = cur.fetchone()[0]
    
    # Count surveillances
    cur.execute("SELECT COUNT(*) FROM surveillance WHERE id_prof = %s", (prof_id,))
    total_surveil = cur.fetchone()[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <h3>📚 Modules</h3>
            <div class="kpi">{total_modules}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <h3>📝 Examens</h3>
            <div class="kpi">{total_exams}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card">
            <h3>👁️ Surveillances</h3>
            <div class="kpi">{total_surveil}</div>
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
        exam_df = pd.DataFrame(exams, columns=['ID', 'Module', 'Salle', 'Date', 'Heure début', 'Heure fin'])
        st.dataframe(exam_df, use_container_width=True)
    else:
        st.info("Aucun examen assigné pour le moment.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ================== MY SURVEILLANCES ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("👁️ Mes Surveillances")
    
    cur.execute("""
        SELECT 
            s.id_surv,
            e.id_examen,
            m.nom AS module_name,
            c.date_exam,
            c.heure_debut,
            COUNT(i.id_etud) AS nb_students
        FROM surveillance s
        JOIN examen e ON s.id_examen = e.id_examen
        JOIN module m ON e.id_module = m.id_module
        JOIN creneau c ON e.id_creneau = c.id_creneau
        LEFT JOIN inscription i ON i.id_module = e.id_module
        WHERE s.id_prof = %s
        GROUP BY s.id_surv, e.id_examen, m.nom, c.date_exam, c.heure_debut
        ORDER BY c.date_exam, c.heure_debut
    """, (prof_id,))
    
    surveillances = cur.fetchall()
    if surveillances:
        surv_df = pd.DataFrame(surveillances, columns=['ID', 'Exam ID', 'Module', 'Date', 'Heure', 'Nb Étudiants'])
        st.dataframe(surv_df, use_container_width=True)
    else:
        st.info("Aucune surveillance assignée pour le moment.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ================== MODULES ==================
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📚 Modules du Département")
    
    cur.execute("""
        SELECT 
            m.id_module,
            m.nom,
            f.nom AS formation,
            COUNT(i.id_etud) AS nb_inscrits
        FROM module m
        JOIN formation f ON m.id_form = f.id_form
        LEFT JOIN inscription i ON i.id_module = m.id_module
        WHERE f.id_dept = %s
        GROUP BY m.id_module, m.nom, f.nom
        ORDER BY f.nom, m.nom
    """, (id_dept,))
    
    modules = cur.fetchall()
    if modules:
        mod_df = pd.DataFrame(modules, columns=['Module ID', 'Module', 'Formation', 'Inscrits'])
        st.dataframe(mod_df, use_container_width=True)
    else:
        st.info("Aucun module trouvé dans votre département.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    cur.close()
    conn.close()

except Exception as e:
    st.error(f"Erreur lors du chargement des données: {e}")

# ================== FOOTER ==================
st.caption("Projet universitaire — Interface Enseignant")