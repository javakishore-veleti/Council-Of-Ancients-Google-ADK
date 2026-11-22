-- Optional bootstrap for the local Council Postgres database.
-- App default remains SQLite; this runs only when the postgres compose profile is enabled.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
