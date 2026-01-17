-- Schema for EDT Universitaire (PostgreSQL)
-- Creates tables, constraints and trigger functions for critical rules.

-- Enable required extension for certain index types (if not available, skip)
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Departments
CREATE TABLE IF NOT EXISTS departement (
	id_dept SERIAL PRIMARY KEY,
	nom TEXT NOT NULL UNIQUE
);

-- Formations
CREATE TABLE IF NOT EXISTS formation (
	id_form SERIAL PRIMARY KEY,
	nom TEXT NOT NULL,
	id_dept INTEGER NOT NULL REFERENCES departement(id_dept) ON DELETE CASCADE,
	nb_modules INTEGER DEFAULT 0
);

-- Professors
CREATE TABLE IF NOT EXISTS professeur (
	id_prof SERIAL PRIMARY KEY,
	nom TEXT NOT NULL,
	prenom TEXT,
	id_dept INTEGER REFERENCES departement(id_dept),
	specialite TEXT,
	password TEXT DEFAULT '124'
);

-- Rooms / locations
CREATE TABLE IF NOT EXISTS salle (
	id_salle SERIAL PRIMARY KEY,
	nom TEXT NOT NULL,
	capacite INTEGER NOT NULL,
	type TEXT,
	batiment TEXT
);

-- Modules
CREATE TABLE IF NOT EXISTS module (
	id_module SERIAL PRIMARY KEY,
	nom TEXT NOT NULL,
	credits INTEGER DEFAULT 3,
	id_form INTEGER REFERENCES formation(id_form),
	pre_req_id INTEGER REFERENCES module(id_module)
);

-- Students
CREATE TABLE IF NOT EXISTS etudiant (
	id_etud SERIAL PRIMARY KEY,
	nom TEXT NOT NULL,
	prenom TEXT,
	id_form INTEGER REFERENCES formation(id_form),
	promo INTEGER,
	password TEXT DEFAULT '124'
);

-- Inscriptions (students -> modules)
CREATE TABLE IF NOT EXISTS inscription (
	id_insc SERIAL PRIMARY KEY,
	id_etud INTEGER REFERENCES etudiant(id_etud) ON DELETE CASCADE,
	id_module INTEGER REFERENCES module(id_module) ON DELETE CASCADE,
	note NUMERIC,
	UNIQUE(id_etud, id_module)
);

-- Timeslots (creneaux)
CREATE TABLE IF NOT EXISTS creneau (
	id_creneau SERIAL PRIMARY KEY,
	date_exam DATE NOT NULL,
	heure_debut TIME NOT NULL,
	heure_fin TIME NOT NULL
);

-- Exams (scheduled or to-be-scheduled)
CREATE TABLE IF NOT EXISTS examen (
	id_examen SERIAL PRIMARY KEY,
	id_module INTEGER REFERENCES module(id_module) ON DELETE CASCADE,
	id_prof INTEGER REFERENCES professeur(id_prof),
	id_salle INTEGER REFERENCES salle(id_salle),
	id_creneau INTEGER REFERENCES creneau(id_creneau),
	duree_minutes INTEGER DEFAULT 90
);

-- Surveillance assignments (which professor supervises which exam)
CREATE TABLE IF NOT EXISTS surveillance (
	id_surv SERIAL PRIMARY KEY,
	id_examen INTEGER REFERENCES examen(id_examen) ON DELETE CASCADE,
	id_prof INTEGER REFERENCES professeur(id_prof)
);

-- Indexes to speed up queries
CREATE INDEX IF NOT EXISTS idx_inscription_module ON inscription(id_module);
CREATE INDEX IF NOT EXISTS idx_inscription_etud ON inscription(id_etud);
CREATE INDEX IF NOT EXISTS idx_examen_prof ON examen(id_prof);
CREATE INDEX IF NOT EXISTS idx_examen_creneau ON examen(id_creneau);
CREATE INDEX IF NOT EXISTS idx_creneau_date ON creneau(date_exam);

-- Partial index example: frequently query rooms with capacity >= X
CREATE INDEX IF NOT EXISTS idx_salle_capacite ON salle(capacite);

-- Trigger functions for critical constraints
-- 1) Enforce per-student: max 1 exam per day
-- 2) Enforce per-professor: max 3 exams per day
-- 3) Enforce room capacity vs enrolled students

-- Function: check constraints before inserting/updating examen
CREATE OR REPLACE FUNCTION fn_check_examen_constraints()
RETURNS TRIGGER AS $$
DECLARE
	exam_date DATE;
	student_count INTEGER;
	conflict_count INTEGER;
	prof_count INTEGER;
BEGIN
	IF NEW.id_creneau IS NULL THEN
		-- not scheduled yet, allow
		RETURN NEW;
	END IF;

	SELECT date_exam INTO exam_date FROM creneau WHERE id_creneau = NEW.id_creneau;

	-- 1) Room capacity check
	IF NEW.id_salle IS NOT NULL THEN
		SELECT COUNT(*) INTO student_count
		FROM inscription i
		WHERE i.id_module = NEW.id_module;

		IF student_count IS NULL THEN
			student_count := 0;
		END IF;

		PERFORM 1 FROM salle s WHERE s.id_salle = NEW.id_salle AND s.capacite >= student_count;
		IF NOT FOUND THEN
			RAISE EXCEPTION 'Room % capacity insufficient for module % (students=%)', NEW.id_salle, NEW.id_module, student_count;
		END IF;
	END IF;

	-- 2) Student conflict: each student max 1 exam per day
	SELECT COUNT(*) INTO conflict_count
	FROM (
		SELECT i.id_etud
		FROM inscription i
		JOIN examen e ON e.id_module = i.id_module
		JOIN creneau c ON c.id_creneau = e.id_creneau
		WHERE c.date_exam = exam_date
		  AND i.id_etud IN (SELECT id_etud FROM inscription WHERE id_module = NEW.id_module)
		  AND (e.id_examen IS DISTINCT FROM NEW.id_examen)
		LIMIT 1
	) t;

	IF conflict_count > 0 THEN
		RAISE EXCEPTION 'Student conflict: some students of module % already have an exam on %', NEW.id_module, exam_date;
	END IF;

	-- 3) Professor limit: max 3 exams per day
	IF NEW.id_prof IS NOT NULL THEN
		SELECT COUNT(*) INTO prof_count
		FROM examen e
		JOIN creneau c ON c.id_creneau = e.id_creneau
		WHERE e.id_prof = NEW.id_prof
		  AND c.date_exam = exam_date
		  AND (e.id_examen IS DISTINCT FROM NEW.id_examen);

		IF prof_count >= 3 THEN
			RAISE EXCEPTION 'Professor % would exceed 3 exams on %', NEW.id_prof, exam_date;
		END IF;
	END IF;

	RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger on examen
DROP TRIGGER IF EXISTS trg_examen_constraints ON examen;
CREATE TRIGGER trg_examen_constraints
BEFORE INSERT OR UPDATE ON examen
FOR EACH ROW EXECUTE FUNCTION fn_check_examen_constraints();

-- Sample seed data (minimal set to test the system)
-- Departments
INSERT INTO departement (nom) VALUES ('Informatique') ON CONFLICT DO NOTHING;
INSERT INTO departement (nom) VALUES ('Mathematiques') ON CONFLICT DO NOTHING;

-- Formations
INSERT INTO formation (nom, id_dept, nb_modules) VALUES ('Licence Info', 1, 😎 ON CONFLICT DO NOTHING;
INSERT INTO formation (nom, id_dept, nb_modules) VALUES ('Licence Maths', 2, 😎 ON CONFLICT DO NOTHING;

-- Rooms
INSERT INTO salle (nom, capacite, type, batiment) VALUES ('Amphi A', 120, 'amphi', 'B1') ON CONFLICT DO NOTHING;
INSERT INTO salle (nom, capacite, type, batiment) VALUES ('Salle 101', 30, 'td', 'B2') ON CONFLICT DO NOTHING;
INSERT INTO salle (nom, capacite, type, batiment) VALUES ('Salle 102', 25, 'td', 'B2') ON CONFLICT DO NOTHING;

-- Professors
INSERT INTO professeur (nom, prenom, id_dept, specialite) VALUES ('Ben', 'Ali', 1, 'Algo') ON CONFLICT DO NOTHING;
INSERT INTO professeur (nom, prenom, id_dept, specialite) VALUES ('Smith', 'John', 2, 'Analyse') ON CONFLICT DO NOTHING;

-- Modules
INSERT INTO module (nom, credits, id_form) VALUES ('Algo', 4, 1) ON CONFLICT DO NOTHING;
INSERT INTO module (nom, credits, id_form) VALUES ('BD', 3, 1) ON CONFLICT DO NOTHING;
INSERT INTO module (nom, credits, id_form) VALUES ('Analyse', 4, 2) ON CONFLICT DO NOTHING;

-- Timeslots
INSERT INTO creneau (date_exam, heure_debut, heure_fin) VALUES ('2026-01-20', '09:00', '11:00') ON CONFLICT DO NOTHING;
INSERT INTO creneau (date_exam, heure_debut, heure_fin) VALUES ('2026-01-20', '14:00', '16:00') ON CONFLICT DO NOTHING;
INSERT INTO creneau (date_exam, heure_debut, heure_fin) VALUES ('2026-01-21', '09:00', '11:00') ON CONFLICT DO NOTHING;

-- Students (small sample)
INSERT INTO etudiant (nom, prenom, id_form, promo) VALUES ('Kacem','Rami',1,2026) ON CONFLICT DO NOTHING;
INSERT INTO etudiant (nom, prenom, id_form, promo) VALUES ('Zara','Lina',1,2026) ON CONFLICT DO NOTHING;
INSERT INTO etudiant (nom, prenom, id_form, promo) VALUES ('Omar','Youssef',2,2026) ON CONFLICT DO NOTHING;

-- Inscriptions
INSERT INTO inscription (id_etud, id_module) VALUES (1,1) ON CONFLICT DO NOTHING;
INSERT INTO inscription (id_etud, id_module) VALUES (2,1) ON CONFLICT DO NOTHING;
INSERT INTO inscription (id_etud, id_module) VALUES (3,3) ON CONFLICT DO NOTHING;

-- Example un-scheduled examen records (to be scheduled by algorithm)
INSERT INTO examen (id_module, id_prof) VALUES (1,1) ON CONFLICT DO NOTHING;
INSERT INTO examen (id_module, id_prof) VALUES (2,1) ON CONFLICT DO NOTHING;

-- End of schema
