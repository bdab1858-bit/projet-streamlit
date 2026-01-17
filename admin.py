import streamlit as st
import pandas as pd
from algorithme import generate_exam_schedule, persist_schedule_to_db
from db_queries import count_examens, count_salles, count_etudiants, exams_per_day, count_conflicts, count_salles_utilisees

# Role-based access control
if st.session_state.get('user_role') != 'admin':
    st.error("Accès refusé. Seuls les administrateurs peuvent accéder à cette page.")
    st.stop()

# precompute totals for dynamic defaults
_TOTAL_SALLES = count_salles()

# ================== CONFIG PAGE ==================
st.set_page_config(
    page_title="Admin | Optimisation Examens",
    page_icon="🛠",
    layout="wide"
)

# ================== STYLE PRO ==================
st.markdown("""
<style>
.stApp {
    background-color: #F1F4F9;
    font-family: 'Segoe UI', sans-serif;
}

/* HEADER */
.header {
    background: linear-gradient(90deg, #5B9DFF, #6EC6FF);
    padding: 35px;
    border-radius: 22px;
    color: white;
    margin-bottom: 35px;
    box-shadow: 0px 15px 35px rgba(0,0,0,0.15);
}

.subtitle {
    font-size: 18px;
    opacity: 0.9;
}

/* CARDS */
.card {
    background-color: white;
    padding: 28px;
    border-radius: 22px;
    box-shadow: 0px 15px 35px rgba(0,0,0,0.1);
    margin-bottom: 25px;
}

/* KPI */
.kpi {
    font-size: 38px;
    font-weight: bold;
    color: #5B9DFF;
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(90deg, #5B9DFF, #3B6EDC);
    color: white;
    border-radius: 18px;
    padding: 14px 32px;
    font-size: 17px;
    font-weight: 600;
    border: none;
}

.stButton>button:hover {
    transform: scale(1.03);
}

/* INPUTS */
div[data-baseweb="select"] > div,
.stNumberInput input {
    background-color: #EEF3FF;
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("""
<div class="header">
    <h1>🛠 Administrateur des Examens</h1>
    <div class="subtitle">
        Dashboard de pilotage — Planification & Optimisation des examens
    </div>
</div>
""", unsafe_allow_html=True)

# ================== KPI ==================
col1, col2, col3 = st.columns(3)

with col1:
    total_exams = count_examens()
    st.markdown(f"""
    <div class="card">
        <h3>📘 Examens planifiés</h3>
        <div class="kpi">{total_exams}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    conflicts = count_conflicts()
    st.markdown(f"""
    <div class="card">
        <h3>⚠️ Conflits détectés</h3>
        <div class="kpi">{conflicts}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    salles_used = count_salles_utilisees()
    total_salles = count_salles()
    st.markdown(f"""
    <div class="card">
        <h3>🏫 Salles utilisées</h3>
        <div class="kpi">{salles_used} / {total_salles}</div>
    </div>
    """, unsafe_allow_html=True)

# ================== CONFIGURATION ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("⚙️ Configuration de la planification")

c1, c2, c3 = st.columns(3)

with c1:
    periode = st.selectbox("📅 Période d'examens", ["Semestre 1", "Semestre 2"])

with c2:
    nb_salles = st.number_input("🏫 Nombre de salles", min_value=1, value=_TOTAL_SALLES)

with c3:
    duree = st.selectbox("⏱ Durée d’un examen", ["1h", "1h30", "2h"])

st.markdown('</div>', unsafe_allow_html=True)

# ================== GENERATION ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🚀 Lancement de l’optimisation")

auto_persist = st.checkbox("💾 Enregistrer automatiquement dans la base de données", value=True)

if st.button("⚙️ Générer l’emploi du temps"):
    try:
        result = generate_exam_schedule()
        st.success("Emploi du temps généré")

        # normalize result into DataFrame
        df = pd.DataFrame(result)
        if not df.empty:
            display_df = df.rename(columns={
                "module": "Module",
                "salle": "Salle",
                "date": "Date",
                "heure": "Heure",
            })

            st.dataframe(display_df[["Module", "Salle", "Date", "Heure"]], use_container_width=True)

            csv = display_df[["Module", "Salle", "Date", "Heure"]].to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Télécharger CSV", csv, file_name="emploi_du_temps.csv", mime="text/csv")

            # show unscheduled modules if any
            if "Salle" in display_df.columns:
                uns = display_df[display_df["Salle"].isnull()]
                if not uns.empty:
                    st.warning(f"{len(uns)} modules non planifiés")
                    st.table(uns[["Module"]].assign(Note="Not scheduled"))

            # persist if requested
            if auto_persist:
                try:
                    persist_schedule_to_db(result)
                    st.success("Emploi du temps enregistré en base de données")
                except Exception as e:
                    st.error(f"Erreur lors de l'enregistrement en base: {e}")
        else:
            st.info("Aucun module trouvé dans la base de données.")
    except Exception as e:
        st.error(f"Erreur lors de la génération: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ================== DASHBOARD DATA ==================
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📊 Répartition des examens par jour")

rows = exams_per_day()
if rows:
    df = pd.DataFrame(rows, columns=["Date", "Examens"]) 
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime('%Y-%m-%d')
    st.bar_chart(df.set_index("Date"))
else:
    st.info("Aucun examen planifié pour l'instant.")

st.markdown('</div>', unsafe_allow_html=True)

# ================== FOOTER ==================
st.caption("Projet universitaire — Plateforme d’Optimisation des Emplois du Temps d’Examens")