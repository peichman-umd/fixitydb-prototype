CREATE TABLE binaries (
  uri varchar primary key,
  last_modified timestamp with time zone,
  size integer,
  digest varchar
);

CREATE TABLE results (
  id serial primary key,
  binary_uri varchar references binaries(uri),
  outcome varchar,
  time timestamp with time zone,
  size integer,
  digest varchar,
  -- we duplicate these here instead of using a view with a join since
  -- we want a snapshot of the expected size and digest *at the time of
  -- the fixity check*, and the binaries table only tracks the latest
  -- values for those fields
  last_modified timestamp with time zone,
  expected_size integer,
  expected_digest varchar
);

-- view of least recently checked binaries
-- use "NULLS FIRST" to hoist resources that have never been fixity checked to the top of the list
-- include uri in the "ORDER BY" clause to guarantee a stable ordering if two binaries have the same
-- last modified and last checked timestamps
CREATE VIEW least_recent (uri, last_modified, latest_check_time) AS
  SELECT uri, last_modified, (SELECT time FROM results WHERE binary_uri = uri ORDER BY time DESC LIMIT 1)
  FROM binaries ORDER BY time ASC NULLS FIRST, last_modified ASC, uri;

-- view of statistics for each URI
CREATE VIEW stats AS
  SELECT
    uri,
    (SELECT time FROM results WHERE binary_uri = uri ORDER BY time DESC LIMIT 1) AS latest_check_time,
    (SELECT COUNT(*) FROM results WHERE uri = binary_uri) AS total_checks,
    (SELECT COUNT(*) FROM results WHERE uri = binary_uri AND outcome = 'SUCCESS') AS successes,
    (SELECT COUNT(*) FROM results WHERE uri = binary_uri AND outcome != 'SUCCESS') AS failures
  FROM binaries
  ORDER BY total_checks DESC, uri;

-- view of failed fixity checks, most recent first
CREATE VIEW failures AS SELECT * FROM results WHERE outcome != 'SUCCESS' ORDER BY time DESC, uri;
