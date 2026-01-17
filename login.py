import streamlit as st
from bd import get_connection

st.set_page_config(page_title="Login", layout="centered")

# Hide sidebar
st.markdown("""
<style>
[data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

st.title("🔐 Connexion — Plateforme EDT")

matricule = st.text_input("Matricule")
mot_de_passe = st.text_input("Mot de passe", type="password")

if st.button("Se connecter"):
    if not matricule or not mot_de_passe:
        st.error("Veuillez remplir tous les champs.")
        st.stop()

    try:
        conn = get_connection()
        cur = conn.cursor()

        # ================== ETUDIANT ==================
        cur.execute("""
            SELECT id_etud
            FROM etudiant
            WHERE matricule = %s AND mot_de_passe = %s
        """, (matricule, mot_de_passe))

        etud = cur.fetchone()

        if etud:
            st.session_state.user_role = "etudiant"
            st.session_state.user_id = etud[0]
            st.switch_page("pages/etudiant.py")

        # ================== PROFESSEUR & ROLES ==================
        cur.execute("""
            SELECT id_prof, role
            FROM professeur
            WHERE matricule = %s AND mot_de_passe = %s
        """, (matricule, mot_de_passe))

        prof = cur.fetchone()

        if not prof:
            st.error("Identifiants incorrects.")
            st.stop()

        user_id, role = prof
        st.session_state.user_id = user_id
        st.session_state.user_role = role

        # ================== REDIRECTION ==================
        if role == "enseignant":
            st.switch_page("pages/enseignant.py")
        elif role == "chef_dept":
            st.switch_page("pages/chef_dept.py")
        elif role == "doyen":
            st.switch_page("pages/doyen.py")
        elif role == "admin":
            st.switch_page("pages/admin.py")
        else:
            st.error("Rôle inconnu.")

    except Exception as e:
        st.error(f"Erreur : {e}")
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass