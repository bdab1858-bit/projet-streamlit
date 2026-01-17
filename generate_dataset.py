import random
from bd import get_connection

def bulk_generate(num_students=2000, num_modules=200, avg_modules_per_student=6):
    conn = get_connection()
    cur = conn.cursor()

    # ensure some modules exist
    cur.execute('SELECT COUNT(*) FROM module')
    mcount = cur.fetchone()[0]
    if mcount < num_modules:
        for i in range(mcount + 1, num_modules + 1):
            cur.execute('INSERT INTO module (nom, credits, id_form) VALUES (%s, %s, %s)',
                        (f'Module_{i}', 3, 1))
    conn.commit()

    # load module ids
    cur.execute('SELECT id_module FROM module')
    modules = [r[0] for r in cur.fetchall()]

    # generate students
    cur.execute('SELECT COUNT(*) FROM etudiant')
    scount = cur.fetchone()[0]
    start = scount + 1

    batch = []
    for i in range(start, start + num_students):
        nom = f'Etud{i}'
        prenom = f'P{i}'
        batch.append((nom, prenom, 1, 2026))
        if len(batch) >= 500:
            cur.executemany('INSERT INTO etudiant (nom, prenom, id_form, promo) VALUES (%s,%s,%s,%s)', batch)
            conn.commit()
            batch = []
    if batch:
        cur.executemany('INSERT INTO etudiant (nom, prenom, id_form, promo) VALUES (%s,%s,%s,%s)', batch)
        conn.commit()

    # fetch new student ids
    cur.execute('SELECT id_etud FROM etudiant ORDER BY id_etud')
    students = [r[0] for r in cur.fetchall()]

    # generate inscriptions: each student signs up to random modules
    ins_batch = []
    for sid in students:
        k = max(1, int(random.gauss(avg_modules_per_student, 1)))
        chosen = random.sample(modules, min(k, len(modules)))
        for mid in chosen:
            ins_batch.append((sid, mid))
        if len(ins_batch) >= 1000:
            cur.executemany('INSERT INTO inscription (id_etud, id_module) VALUES (%s,%s) ON CONFLICT DO NOTHING', ins_batch)
            conn.commit()
            ins_batch = []
    if ins_batch:
        cur.executemany('INSERT INTO inscription (id_etud, id_module) VALUES (%s,%s) ON CONFLICT DO NOTHING', ins_batch)
        conn.commit()

    cur.close()
    conn.close()

if __name__ == '_main_':
    print('Generating dataset (this may take a while)')
    bulk_generate(num_students=5000, num_modules=300, avg_modules_per_student=6)
    print('Done')