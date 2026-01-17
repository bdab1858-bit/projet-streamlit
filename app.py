import streamlit as st

st.set_page_config(
    page_title="Optimisation Examens",
    page_icon="🎓",
    layout="wide"
)

# ensure session state keys exist
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

st.title("🎓 Plateforme d’Optimisation des Emplois du Temps d’Examens")
st.caption("Projet universitaire")

st.sidebar.title("🎓 Menu")
st.sidebar.markdown("### Accès")
if st.sidebar.button("Se connecter"):
    st.switch_page('pages/login.py')
st.sidebar.markdown("---")
st.sidebar.markdown("Ou choisissez votre rôle (accès direct):")

role = st.sidebar.selectbox(
    "",
    [
        "Administrateur examens",
        "Doyen / Vice-doyen",
        "Chef de département",
        "Étudiant / Professeur"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Université — 2025")

if role == "Administrateur examens":
    st.switch_page("pages/admin.py")
elif role == "Doyen / Vice-doyen":
    st.switch_page("pages/doyen.py")
elif role == "Chef de département":
    st.switch_page("pages/chef_dept.py")
else:
    st.switch_page("pages/etudiant.py")