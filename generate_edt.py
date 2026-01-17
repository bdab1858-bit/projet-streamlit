import psycopg2
from collections import defaultdict
import random

# ==============================
# 1️⃣ Connexion PostgreSQL
# ==============================
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="edt_universitaire",
        user="postgres",
        password="0000",
        port="5432"
    )

conn = get_connection()
cur = conn.cursor()

# ==============================
# 2️⃣ Récupération des données
# ==============================

# Examens (sans nb_etudiants)
cur.execute("""
    SELECT id_examen, id_module
    FROM examen
""")
examens = cur.fetchall()

# Salles
cur.execute("SELECT id_salle, capacite FROM salle")
salles = cur.fetchall()

# Professeurs (CORRIGÉ)
cur.execute("SELECT id_prof, id_dept FROM professeur")
profs = cur.fetchall()

# Inscriptions
cur.execute("SELECT id_etud, id_module FROM inscription")
inscriptions = cur.fetchall()

# Nombre d'étudiants par module (CORRIGÉ)
cur.execute("""
    SELECT id_module, COUNT(id_etud)
    FROM inscription
    GROUP BY id_module
""")
nb_etudiants_par_module = dict(cur.fetchall())

# Module → département (CORRIGÉ)
cur.execute("""
    SELECT m.id_module, f.id_dept
    FROM module m
    JOIN formation f ON m.id_form = f.id_form
""")
module_dept = dict(cur.fetchall())

# ==============================
# 3️⃣ Créneaux et structures
# ==============================
creneaux = ["08:30-10:00", "10:15-11:45", "12:00-13:30", "13:45-15:15"]

etudiant_jour = defaultdict(set)
prof_jour = defaultdict(set)
salle_creneau = defaultdict(set)

planning = []
surveillance_data = []

# ==============================
# 4️⃣ Génération gloutonne
# ==============================
for id_examen, id_module in examens:
    placed = False
    nb_etudiants = nb_etudiants_par_module.get(id_module, 0)

    for c in creneaux:

        # ----- Salle -----
        salle_id = None
        for sid, capacite in salles:
            if c not in salle_creneau[sid] and nb_etudiants <= capacite:
                salle_id = sid
                break
        if salle_id is None:
            continue

        # ----- Professeur -----
        prof_id = None
        random.shuffle(profs)
        for pid, dept_id in profs:
            if (
                c not in prof_jour[pid]
                and dept_id == module_dept.get(id_module)
            ):
                prof_id = pid
                break
        if prof_id is None:
            continue

        # ----- Conflit étudiant -----
        conflict = False
        for etud_id, mod in inscriptions:
            if mod == id_module and c in etudiant_jour[etud_id]:
                conflict = True
                break
        if conflict:
            continue

        # ----- Placement -----
        planning.append((id_examen, c, salle_id, prof_id))
        salle_creneau[salle_id].add(c)
        prof_jour[prof_id].add(c)

        for etud_id, mod in inscriptions:
            if mod == id_module:
                etudiant_jour[etud_id].add(c)

        surveillance_data.append((id_examen, prof_id))
        placed = True
        break

    if not placed:
        print(f"⚠️ Impossible de placer l'examen {id_examen}")

# ==============================
# 5️⃣ Optimisation locale (SAFE)
# ==============================
def calcul_score(pl):
    score = 0
    etud_tmp = defaultdict(set)

    for id_exam, c, _, _ in pl:
        for etud_id, mod in inscriptions:
            if mod == id_exam:
                if c in etud_tmp[etud_id]:
                    score += 10
                else:
                    etud_tmp[etud_id].add(c)
    return score

if len(planning) >= 2:
    score = calcul_score(planning)

    for _ in range(300):
        a, b = random.sample(range(len(planning)), 2)
        planning[a], planning[b] = planning[b], planning[a]
        new_score = calcul_score(planning)

        if new_score <= score:
            score = new_score
        else:
            planning[a], planning[b] = planning[b], planning[a]

# ==============================
# 6️⃣ Insertion en base
# ==============================
for id_examen, creneau, salle_id, prof_id in planning:
    cur.execute("""
        UPDATE examen
        SET id_salle = %s,
            id_prof = %s,
            id_creneau = (
                SELECT id_creneau
                FROM creneau
                WHERE horaire = %s
            )
        WHERE id_examen = %s
    """, (salle_id, prof_id, creneau, id_examen))

for id_examen, id_prof in surveillance_data:
    cur.execute("""
        INSERT INTO surveillance (id_examen, id_prof)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
    """, (id_examen, id_prof))

conn.commit()
cur.close()
conn.close()

print("✅ Planning généré et enregistré avec succès !")