CREATE ROLE authenticator NOINHERIT LOGIN PASSWORD 'foobar';
CREATE ROLE web_anon NOLOGIN;
CREATE ROLE fixity NOLOGIN;

GRANT USAGE ON SCHEMA public TO web_anon, fixity;

-- read-only access for anonymous user
GRANT SELECT ON binaries, results, least_recent, stats TO web_anon;

-- read-only access to views for authenticated user
GRANT SELECT ON least_recent, stats TO fixity;

-- full access to tables for authenticated user
-- for serial columns, need to grant access to the corresponding sequence to the user
GRANT ALL ON binaries, results, results_id_seq TO fixity;

-- authenticator can become these roles
GRANT web_anon, fixity TO authenticator;
