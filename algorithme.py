from bd import get_connection


def generate_exam_schedule():
    """Generate a simple conflict-aware exam schedule.

    Returned schedule items include ids so they can be persisted:
    {id_module, module, id_salle, salle, id_creneau, date, heure}
    """
    conn = get_connection()
    cur = conn.cursor()

    # modules
    cur.execute("SELECT id_module, nom FROM module")
    modules = cur.fetchall()  # list of (id_module, nom)

    # students per module
    module_students = {}
    for m in modules:
        mid = m[0]
        cur.execute("SELECT id_etud FROM inscription WHERE id_module = %s", (mid,))
        rows = cur.fetchall()
        module_students[mid] = set(r[0] for r in rows)

    # salles
    cur.execute("SELECT id_salle, nom, capacite FROM salle")
    salles = cur.fetchall()  # list of (id_salle, nom, capacite)

    # creneaux
    cur.execute("SELECT id_creneau, date_exam, heure_debut, heure_fin FROM creneau ORDER BY date_exam, heure_debut")
    creneaux = cur.fetchall()

    schedule = []
    used_salle_creneau = set()  # (salle_id, creneau_id)
    modules_by_creneau = {}  # creneau_id -> list of module_ids scheduled

    for module in modules:
        mid, mnom = module[0], module[1]
        n_students = len(module_students.get(mid, set()))
        assigned = False

        for c in creneaux:
            cid, date_exam, hd, hf = c

            # check student conflicts with modules already at this creneau
            conflict = False
            for other_mid in modules_by_creneau.get(cid, []):
                if module_students.get(other_mid, set()) & module_students.get(mid, set()):
                    conflict = True
                    break
            if conflict:
                continue

            # try to find a salle with enough capacity and free
            for salle in salles:
                sid, snom, cap = salle
                key = (sid, cid)
                if key in used_salle_creneau:
                    continue
                if cap is not None and n_students > cap:
                    continue

                # assign
                used_salle_creneau.add(key)
                modules_by_creneau.setdefault(cid, []).append(mid)

                schedule.append({
                    "id_module": mid,
                    "module": mnom,
                    "id_salle": sid,
                    "salle": snom,
                    "id_creneau": cid,
                    "date": date_exam,
                    "heure": f"{hd} - {hf}"
                })
                assigned = True
                break

            if assigned:
                break

        if not assigned:
            schedule.append({
                "id_module": mid,
                "module": mnom,
                "id_salle": None,
                "salle": None,
                "id_creneau": None,
                "date": None,
                "heure": None,
                "note": "Not scheduled"
            })

    cur.close()
    conn.close()

    return schedule


def persist_schedule_to_db(schedule, overwrite=True):
    """Persist generated schedule into examen table.

    If an examen for the same module exists, update it when overwrite is True,
    otherwise skip.
    """
    conn = get_connection()
    cur = conn.cursor()

    for item in schedule:
        mid = item.get("id_module")
        sid = item.get("id_salle")
        cid = item.get("id_creneau")

        if mid is None:
            continue

        if sid is None or cid is None:
            # skip unscheduled modules
            continue

        cur.execute("SELECT id_examen FROM examen WHERE id_module = %s", (mid,))
        row = cur.fetchone()
        if row:
            eid = row[0]
            if overwrite:
                cur.execute(
                    "UPDATE examen SET id_salle=%s, id_creneau=%s WHERE id_examen=%s",
                    (sid, cid, eid)
                )
        else:
            cur.execute(
                "INSERT INTO examen (id_module, id_salle, id_creneau) VALUES (%s,%s,%s)",
                (mid, sid, cid)
            )

    conn.commit()
    cur.close()
    conn.close()