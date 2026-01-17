"""
Script d'initialisation simplifié - crée les tables basiques et insère les données
"""
import psycopg2
from bd import get_connection
import random
import string

def generate_prof_matricule(prof_id):
    """Génère un matricule de 10 chiffres pour un professeur"""
    return f"{1000000000 + prof_id:010d}"

def generate_etud_matricule(etud_id):
    """Génère un matricule de 14 chiffres (2026 + 8 chiffres) pour un étudiant"""
    return f"202600{etud_id:08d}"

def generate_password_8chars():
    """Génère un mot de passe aléatoire de 8 caractères"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))

def init_database():
    """Initialise la base de données avec schéma et données de test"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        print("🔄 Création des tables...")
        
        # Drop tables if exist (for clean slate)
        tables = ['inscription', 'surveillance', 'examen', 'creneau', 'module', 'etudiant', 'professeur', 'salle', 'formation', 'departement']
        for table in tables:
            try:
                cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
            except:
                pass
        
        # Create tables
        cur.execute("""
            CREATE TABLE departement (
                id_dept SERIAL PRIMARY KEY,
                nom TEXT NOT NULL UNIQUE
            );
        """)
        
        cur.execute("""
            CREATE TABLE formation (
                id_form SERIAL PRIMARY KEY,
                nom TEXT NOT NULL,
                id_dept INTEGER NOT NULL REFERENCES departement(id_dept) ON DELETE CASCADE,
                nb_modules INTEGER DEFAULT 0
            );
        """)
        
        cur.execute("""
            CREATE TABLE professeur (
                id_prof SERIAL PRIMARY KEY,
                nom TEXT NOT NULL,
                prenom TEXT,
                id_dept INTEGER REFERENCES departement(id_dept),
                specialite TEXT,
                password TEXT DEFAULT '1234',
                matricule VARCHAR(10) NOT NULL UNIQUE CHECK (matricule ~ '^[0-9]{10}$'),
                mot_de_passe VARCHAR(😎 NOT NULL CHECK (char_length(mot_de_passe) = 😎
            );
        """)
        
        cur.execute("""
            CREATE TABLE salle (
                id_salle SERIAL PRIMARY KEY,
                nom TEXT NOT NULL,
                capacite INTEGER NOT NULL,
                type TEXT,
                batiment TEXT
            );
        """)
        
        cur.execute("""
            CREATE TABLE module (
                id_module SERIAL PRIMARY KEY,
                nom TEXT NOT NULL,
                credits INTEGER DEFAULT 3,
                id_form INTEGER REFERENCES formation(id_form),
                pre_req_id INTEGER REFERENCES module(id_module)
            );
        """)
        
        cur.execute("""
            CREATE TABLE etudiant (
                id_etud SERIAL PRIMARY KEY,
                nom TEXT NOT NULL,
                prenom TEXT,
                id_form INTEGER REFERENCES formation(id_form),
                promo INTEGER,
                password TEXT DEFAULT '1234',
                matricule VARCHAR(14) NOT NULL UNIQUE CHECK (matricule ~ '^[0-9]{4}[0-9]{10}$'),
                mot_de_passe VARCHAR(😎 NOT NULL CHECK (char_length(mot_de_passe) = 😎
            );
        """)
        
        cur.execute("""
            CREATE TABLE inscription (
                id_insc SERIAL PRIMARY KEY,
                id_etud INTEGER REFERENCES etudiant(id_etud) ON DELETE CASCADE,
                id_module INTEGER REFERENCES module(id_module) ON DELETE CASCADE,
                note NUMERIC,
                UNIQUE(id_etud, id_module)
            );
        """)
        
        cur.execute("""
            CREATE TABLE creneau (
                id_creneau SERIAL PRIMARY KEY,
                date_exam DATE NOT NULL,
                heure_debut TIME NOT NULL,
                heure_fin TIME NOT NULL
            );
        """)
        
        cur.execute("""
            CREATE TABLE examen (
                id_examen SERIAL PRIMARY KEY,
                id_module INTEGER REFERENCES module(id_module) ON DELETE CASCADE,
                id_prof INTEGER REFERENCES professeur(id_prof),
                id_salle INTEGER REFERENCES salle(id_salle),
                id_creneau INTEGER REFERENCES creneau(id_creneau),
                duree_minutes INTEGER DEFAULT 90
            );
        """)
        
        cur.execute("""
            CREATE TABLE surveillance (
                id_surv SERIAL PRIMARY KEY,
                id_examen INTEGER REFERENCES examen(id_examen) ON DELETE CASCADE,
                id_prof INTEGER REFERENCES professeur(id_prof)
            );
        """)
        
        # Create indexes
        cur.execute("CREATE INDEX IF NOT EXISTS idx_inscription_module ON inscription(id_module);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_inscription_etud ON inscription(id_etud);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_examen_prof ON examen(id_prof);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_examen_creneau ON examen(id_creneau);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_creneau_date ON creneau(date_exam);")
        
        conn.commit()
        print("✅ Tables créées avec succès!")
        
        # Insert test data
        print("📝 Insertion des données de test...")
        
        # Departments
        cur.execute("""
            INSERT INTO departement (nom) VALUES
            ('Informatique'),
            ('Mathématiques'),
            ('Physique')
        """)
        conn.commit()
        
        # Formations
        cur.execute("""
            INSERT INTO formation (nom, id_dept, nb_modules) VALUES
            ('L1 Informatique', 1, 😎,
            ('L2 Informatique', 1, 😎,
            ('L1 Mathématiques', 2, 😎,
            ('L1 Physique', 3, 😎
        """)
        conn.commit()
        
        # Professors (with different roles and passwords)
        prof_data = [
            ('Admin', 'Système', 1, 'Administrator', 'admin123'),
            ('Chef', 'Département', 1, 'Chef de département', 'chef123'),
            ('Doyen', 'Académique', 2, 'Doyen', 'doyen123'),
            ('Dupont', 'Jean', 1, 'Programmation', 'prof_dupont'),
            ('Martin', 'Marie', 1, 'Bases de données', 'prof_martin'),
            ('Bernard', 'Pierre', 2, 'Algèbre', 'prof_bernard'),
            ('Thomas', 'Sophie', 3, 'Physique quantique', 'prof_thomas')
        ]
        
        for idx, (nom, prenom, id_dept, specialite, password) in enumerate(prof_data, 1):
            matricule = generate_prof_matricule(idx)
            mot_de_passe = generate_password_8chars()
            cur.execute(
                """INSERT INTO professeur (nom, prenom, id_dept, specialite, password, matricule, mot_de_passe)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (nom, prenom, id_dept, specialite, password, matricule, mot_de_passe)
            )
        conn.commit()
        cur.execute("""
            INSERT INTO salle (nom, capacite, type, batiment) VALUES
            ('A1', 50, 'Amphithéâtre', 'Bâtiment A'),
            ('A2', 50, 'Amphithéâtre', 'Bâtiment A'),
            ('B1', 30, 'Classe', 'Bâtiment B'),
            ('B2', 30, 'Classe', 'Bâtiment B'),
            ('C1', 100, 'Grand amphithéâtre', 'Bâtiment C')
        """)
        conn.commit()
        
        # Timeslots
        cur.execute("""
            INSERT INTO creneau (date_exam, heure_debut, heure_fin) VALUES
            ('2026-01-20', '08:00', '10:00'),
            ('2026-01-20', '10:15', '12:15'),
            ('2026-01-20', '14:00', '16:00'),
            ('2026-01-21', '08:00', '10:00'),
            ('2026-01-21', '10:15', '12:15'),
            ('2026-01-22', '08:00', '10:00')
        """)
        conn.commit()
        
        # Modules
        cur.execute("""
            INSERT INTO module (nom, credits, id_form) VALUES
            ('Programmation Python', 3, 1),
            ('Bases de données SQL', 3, 1),
            ('Réseaux', 3, 1),
            ('Algorithmique', 3, 1),
            ('Algèbre linéaire', 3, 3),
            ('Calcul différentiel', 3, 3),
            ('Mécanique classique', 3, 4),
            ('Thermodynamique', 3, 4)
        """)
        conn.commit()
        
        # Students (with individual passwords and matricules)
        etud_data = [
            ('Ahmed', 'Ali', 1, 2026, 'ahmed2026'),
            ('Fatima', 'Zahra', 1, 2026, 'fatima2026'),
            ('Karim', 'Hassan', 1, 2026, 'karim2026'),
            ('Nadia', 'Amine', 1, 2026, 'nadia2026'),
            ('Moussa', 'Ibrahim', 2, 2025, 'moussa2025'),
            ('Leila', 'Samir', 3, 2026, 'leila2026'),
            ('Omar', 'Khalid', 4, 2026, 'omar2026'),
            ('guerfi', 'amira', 4, 2026, 'amira2026'),
            ('cheradi', 'manel', 2, 2025, 'manel'),
            ('Ahlem', 'ouzeddam', 3, 2022, 'ahlem2026')
        ]
        
        for idx, (nom, prenom, id_form, promo, password) in enumerate(etud_data, 1):
            matricule = generate_etud_matricule(idx)
            mot_de_passe = generate_password_8chars()
            cur.execute(
                """INSERT INTO etudiant (nom, prenom, id_form, promo, password, matricule, mot_de_passe)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (nom, prenom, id_form, promo, password, matricule, mot_de_passe)
            )
        
        # Inscriptions (student enrollments)
        cur.execute("""
            INSERT INTO inscription (id_etud, id_module) VALUES
            (1, 1), (1, 2), (1, 3), (1, 4),
            (2, 1), (2, 2), (2, 3), (2, 4),
            (3, 1), (3, 2), (3, 4),
            (4, 2), (4, 3), (4, 4),
            (5, 1), (5, 2), (5, 3), (5, 4),
            (6, 5), (6, 6),
            (7, 7), (7, 😎,
            (8, 7), (8, 😎,
            (9, 1), (9, 2), (9, 3), (9, 4),
            (10, 5), (10, 6)
        """)
        
        conn.commit()
        print("✅ Données de test insérées avec succès!")
        
        # Display test credentials
        print("\n" + "="*60)
        print("🔑 IDENTIFIANTS DE TEST UNIQUES:")
        print("="*60)
        
        print("\n👨‍🎓 ÉTUDIANTS:")
        print("  1. Ahmed Ali - Mot de passe: ahmed2026")
        print("  2. Fatima Zahra - Mot de passe: fatima2026")
        print("  3. Karim Hassan - Mot de passe: karim2026")
        print("  4. Nadia Amine - Mot de passe: nadia2026")
        print("  5. Moussa Ibrahim - Mot de passe: moussa2025")
        print("  6. Leila Samir - Mot de passe: leila2026")
        print("  7. Omar Khalid - Mot de passe: omar2026")
        print("  8. Yasmine Bilal - Mot de passe: yasmine2026")
        print("  9. Youssef Mohamed - Mot de passe: youssef2025")
        print("  10. Sara Tahir - Mot de passe: sara2026")
        
        print("\n🔐 RÔLES SPÉCIAUX (Professeurs avec rôles):")
        print("  🛡️ ADMIN (ID: 1)")
        print("     Admin Système - Mot de passe: admin123")
        print("  👔 CHEF DE DÉPARTEMENT (ID: 2)")
        print("     Chef Département - Mot de passe: chef123")
        print("  👨‍💼 DOYEN (ID: 3)")
        print("     Doyen Académique - Mot de passe: doyen123")
        
        print("\n👨‍🏫 ENSEIGNANTS NORMAUX:")
        print("  4. Jean Dupont - Mot de passe: prof_dupont")
        print("  5. Marie Martin - Mot de passe: prof_martin")
        print("  6. Pierre Bernard - Mot de passe: prof_bernard")
        print("  7. Sophie Thomas - Mot de passe: prof_thomas")
        
        print("="*60 + "\n")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "_main_":
    init_database()