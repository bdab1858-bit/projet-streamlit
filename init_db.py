"""
Script d'initialisation de la base de données avec données de test
"""
import psycopg2
from bd import get_connection

def init_database():
    """Initialise la base de données avec le schéma et données de test"""
    try:
        # Read and execute SQL schema
        with open('edt_universitaire.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        conn = get_connection()
        cur = conn.cursor()
        
        print("🔄 Exécution du schéma SQL...")
        cur.execute(sql_content)
        conn.commit()
        print("✅ Schéma créé avec succès!")
        
        # Insert test data
        print("📝 Insertion des données de test...")
        
        # Departments
        cur.execute("DELETE FROM departement;")
        cur.execute("""
            INSERT INTO departement (id_dept, nom) VALUES
            (1, 'Informatique'),
            (2, 'Mathématiques'),
            (3, 'Physique')
            ON CONFLICT (id_dept) DO NOTHING;
        """)
        
        # Formations
        cur.execute("DELETE FROM formation;")
        cur.execute("""
            INSERT INTO formation (id_form, nom, id_dept, nb_modules) VALUES
            (1, 'L1 Informatique', 1, 😎,
            (2, 'L2 Informatique', 1, 😎,
            (3, 'L1 Mathématiques', 2, 😎,
            (4, 'L1 Physique', 3, 😎
            ON CONFLICT (id_form) DO NOTHING;
        """)
        
        # Professors
        cur.execute("DELETE FROM professeur;")
        cur.execute("""
            INSERT INTO professeur (id_prof, nom, prenom, id_dept, specialite, password) VALUES
            (1, 'Dupont', 'Jean', 1, 'Programmation', '1234'),
            (2, 'Martin', 'Marie', 1, 'Bases de données', '1234'),
            (3, 'Bernard', 'Pierre', 2, 'Algèbre', '1234'),
            (4, 'Thomas', 'Sophie', 3, 'Physique quantique', '1234')
            ON CONFLICT (id_prof) DO NOTHING;
        """)
        
        # Rooms
        cur.execute("DELETE FROM salle;")
        cur.execute("""
            INSERT INTO salle (id_salle, nom, capacite, type, batiment) VALUES
            (1, 'A1', 50, 'Amphithéâtre', 'Bâtiment A'),
            (2, 'A2', 50, 'Amphithéâtre', 'Bâtiment A'),
            (3, 'B1', 30, 'Classe', 'Bâtiment B'),
            (4, 'B2', 30, 'Classe', 'Bâtiment B'),
            (5, 'C1', 100, 'Grand amphithéâtre', 'Bâtiment C')
            ON CONFLICT (id_salle) DO NOTHING;
        """)
        
        # Timeslots
        cur.execute("DELETE FROM creneau;")
        cur.execute("""
            INSERT INTO creneau (id_creneau, date_exam, heure_debut, heure_fin) VALUES
            (1, '2026-01-20', '08:00', '10:00'),
            (2, '2026-01-20', '10:15', '12:15'),
            (3, '2026-01-20', '14:00', '16:00'),
            (4, '2026-01-21', '08:00', '10:00'),
            (5, '2026-01-21', '10:15', '12:15'),
            (6, '2026-01-22', '08:00', '10:00')
            ON CONFLICT (id_creneau) DO NOTHING;
        """)
        
        # Modules
        cur.execute("DELETE FROM module;")
        cur.execute("""
            INSERT INTO module (id_module, nom, credits, id_form) VALUES
            (1, 'Programmation Python', 3, 1),
            (2, 'Bases de données SQL', 3, 1),
            (3, 'Réseaux', 3, 1),
            (4, 'Algorithmique', 3, 1),
            (5, 'Algèbre linéaire', 3, 3),
            (6, 'Calcul différentiel', 3, 3),
            (7, 'Mécanique classique', 3, 4),
            (8, 'Thermodynamique', 3, 4)
            ON CONFLICT (id_module) DO NOTHING;
        """)
        
        # Students
        cur.execute("DELETE FROM etudiant;")
        cur.execute("""
            INSERT INTO etudiant (id_etud, nom, prenom, id_form, promo, password) VALUES
            (1, 'Ahmed', 'Ali', 1, 2026, '1234'),
            (2, 'Fatima', 'Zahra', 1, 2026, '1234'),
            (3, 'Karim', 'Hassan', 1, 2026, '1234'),
            (4, 'Nadia', 'Amine', 1, 2026, '1234'),
            (5, 'Moussa', 'Ibrahim', 2, 2025, '1234'),
            (6, 'Leila', 'Samir', 3, 2026, '1234'),
            (7, 'Omar', 'Khalid', 4, 2026, '1234'),
            (8, 'Yasmine', 'Bilal', 4, 2026, '1234'),
            (9, 'Youssef', 'Mohamed', 2, 2025, '1234'),
            (10, 'Sara', 'Tahir', 3, 2026, '1234')
            ON CONFLICT (id_etud) DO NOTHING;
        """)
        
        # Inscriptions (student enrollments)
        cur.execute("DELETE FROM inscription;")
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
            ON CONFLICT (id_etud, id_module) DO NOTHING;
        """)
        
        conn.commit()
        print("✅ Données de test insérées avec succès!")
        
        # Display test credentials
        print("\n" + "="*50)
        print("🔑 IDENTIFIANTS DE TEST:")
        print("="*50)
        print("\n👨‍🎓 Étudiants:")
        print("  ID: 1-10, Mot de passe: 1234")
        print("\n👨‍🏫 Enseignants:")
        print("  ID: 1-4, Mot de passe: 1234")
        print("="*50 + "\n")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "_main_":
    init_database()