-- Canonical database schema (reconstructed). Keep in sync with migrations.

CREATE TABLE IF NOT EXISTS users (
  id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
  name text NOT NULL,
  email text DEFAULT NULL,
  created_at timestamp without time zone DEFAULT now(),
  password_hash text DEFAULT NULL,
  PRIMARY KEY (id)
);

-- (Other tables omitted here for brevity; full schema is managed via migrations.)
