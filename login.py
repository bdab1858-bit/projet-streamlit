import streamlit as st
from bd import get_connection

st.set_page_config(page_title="Login", page_icon="🔐", layout="wide")

st.title("🔐 Connexion — Plateforme EDT")

role = st.selectbox("Rôle", [
    "Étudiant",
    "Enseignant",
    "Administrateur examens",
    "Chef de département",
    "Doyen / Vice-doyen"
])

matricule = st.text_input("Matricule")
mot_de_passe = st.text_input("Mot de passe", type="password")

if st.button("Se connecter"):
    if not matricule or not mot_de_passe:
        st.error("Veuillez fournir votre matricule et mot de passe.")
    else:
        try:
            conn = get_connection()
            cur = conn.cursor()

            if role == "Étudiant":
                cur.execute("SELECT id_etud FROM etudiant WHERE matricule = %s AND mot_de_passe = %s", (matricule, mot_de_passe))
                row = cur.fetchone()
                if row:
                    st.success("Connexion réussie en tant qu'étudiant")
                    st.session_state['user_role'] = 'etudiant'
                    st.session_state['user_id'] = row[0]
                    st.switch_page('pages/etudiant.py')
                else:
                    st.error("Matricule ou mot de passe incorrect.")

            else:
                # professor-based roles
                cur.execute("SELECT id_prof FROM professeur WHERE matricule = %s AND mot_de_passe = %s", (matricule, mot_de_passe))
                row = cur.fetchone()
                if not row:
                    st.error("Matricule ou mot de passe incorrect.")
                else:
                    uid = row[0]
                    st.session_state['user_id'] = uid
                    if role == 'Enseignant':
                        st.session_state['user_role'] = 'enseignant'
                        st.success("Connexion réussie en tant qu'enseignant")
                        st.switch_page('pages/enseignant.py')
                    elif role == 'Administrateur examens':
                        st.session_state['user_role'] = 'admin'
                        st.success("Connexion réussie en tant qu'administrateur")
                        st.switch_page('pages/admin.py')
                    elif role == 'Chef de département':
                        st.session_state['user_role'] = 'chef_dept'
                        st.success("Connexion réussie en tant que chef de département")
                        st.switch_page('pages/chef_dept.py')
                    else:
                        st.session_state['user_role'] = 'doyen'
                        st.success("Connexion réussie en tant que doyen")
                        st.switch_page('pages/doyen.py')

        except Exception as e:
            st.error(f"Erreur de connexion à la base: {e}")
        finally:
            try:
                cur.close()
                conn.close()
            except:
                pass