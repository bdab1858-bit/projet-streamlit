from bd import get_connection

def count_examens():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM examen;")
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def count_salles():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM salle;")
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def count_etudiants():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM etudiant;")
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def exams_per_day():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.date_exam, COUNT(e.id_examen) as nb
        FROM examen e
        JOIN creneau c ON e.id_creneau = c.id_creneau
        GROUP BY c.date_exam
        ORDER BY c.date_exam
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def count_conflicts():
    """Return number of student-day conflicts (students who have >1 exam same day)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) FROM (
            SELECT i.id_etud, c.date_exam, COUNT(*) as nb
            FROM inscription i
            JOIN examen e ON i.id_module = e.id_module
            JOIN creneau c ON e.id_creneau = c.id_creneau
            GROUP BY i.id_etud, c.date_exam
            HAVING COUNT(*) > 1
        ) t;
    """)
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def count_salles_utilisees():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(DISTINCT id_salle) FROM examen WHERE id_salle IS NOT NULL;")
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result