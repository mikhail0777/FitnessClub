-- DDL.sql
-- Minimal schema for FitnessClub web app (members, trainers, PT sessions, equipment, rentals, dashboard view)

-- Drop in correct dependency order so this can be re-run safely
DROP VIEW IF EXISTS member_dashboard;

DROP TABLE IF EXISTS equipment_rentals;
DROP TABLE IF EXISTS personal_training_sessions;
DROP TABLE IF EXISTS equipment;
DROP TABLE IF EXISTS trainers;
DROP TABLE IF EXISTS members;

------------------------------------------------------------
-- Core tables
------------------------------------------------------------

CREATE TABLE members (
    id              SERIAL PRIMARY KEY,
    full_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    date_of_birth   DATE,
    gender          TEXT,
    phone           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE trainers (
    id              SERIAL PRIMARY KEY,
    full_name       TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    specialty       TEXT,
    phone           TEXT,
    hired_at        DATE DEFAULT CURRENT_DATE
);

-- Matches your current data: (id, member_id, trainer_id, session_date, session_time, status)
CREATE TABLE personal_training_sessions (
    id              SERIAL PRIMARY KEY,
    member_id       INT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    trainer_id      INT NOT NULL REFERENCES trainers(id),
    session_date    DATE NOT NULL,
    session_time    TIME NOT NULL,
    status          TEXT NOT NULL DEFAULT 'scheduled'
);

-- Matches your current data: (id, room_id, name, status, category, total_quantity, available_quantity)
-- room_id is kept as a plain INT (no FK) because your seed data uses 1 and 2,
-- but there are no room rows in the seed file.
CREATE TABLE equipment (
    id                  SERIAL PRIMARY KEY,
    room_id             INT,
    name                TEXT NOT NULL,
    status              TEXT NOT NULL DEFAULT 'operational',
    category            TEXT,
    total_quantity      INT NOT NULL DEFAULT 1,
    available_quantity  INT NOT NULL DEFAULT 1
);

-- Matches your current data: (id, member_id, equipment_id, rental_date, return_due_date, returned_at)
CREATE TABLE equipment_rentals (
    id                  SERIAL PRIMARY KEY,
    member_id           INT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    equipment_id        INT NOT NULL REFERENCES equipment(id) ON DELETE CASCADE,
    rental_date         DATE NOT NULL,
    return_due_date     DATE,
    returned_at         DATE
);

------------------------------------------------------------
-- Simple dashboard view for members
------------------------------------------------------------

CREATE OR REPLACE VIEW member_dashboard AS
SELECT
    m.id           AS member_id,
    m.full_name,
    m.email,
    m.date_of_birth,
    m.gender,
    m.phone,
    m.created_at,
    -- total PT sessions this member has
    (
        SELECT COUNT(*)
        FROM personal_training_sessions pts
        WHERE pts.member_id = m.id
    ) AS total_pt_sessions,
    -- total equipment rentals this member has made
    (
        SELECT COUNT(*)
        FROM equipment_rentals er
        WHERE er.member_id = m.id
    ) AS total_rentals
FROM members m;

