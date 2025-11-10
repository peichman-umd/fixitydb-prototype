CREATE TABLE binaries (
  uri varchar primary key,
  last_modified timestamp with time zone
);

CREATE TABLE checks (
  id serial primary key,
  binary_uri varchar references binaries(uri),
  success boolean,
  time timestamp with time zone,
  result text
);

-- view of least recently checked binaries
-- use "NULLS FIRST" to hoist resources that have never been fixity checked to the top of the list
-- include uri in the "ORDER BY" clause to guarantee a stable ordering if two binaries have the same
-- last modified and last checked timestamps
CREATE VIEW least_recent (uri, last_modified, latest_check_time) AS
  SELECT uri, last_modified, (SELECT time FROM checks WHERE binary_uri = uri ORDER BY time DESC LIMIT 1)
  FROM binaries ORDER BY time ASC NULLS FIRST, last_modified ASC, uri;

-- view of statistics for each URI
CREATE VIEW stats AS
  SELECT
    uri,
    (SELECT time FROM checks WHERE binary_uri = uri ORDER BY time DESC LIMIT 1) AS latest_check_time,
    (SELECT COUNT(*) FROM checks WHERE uri = binary_uri) AS total_checks,
    (SELECT COUNT(*) FROM checks WHERE uri = binary_uri AND success = 't') AS successes,
    (SELECT COUNT(*) FROM checks WHERE uri = binary_uri AND success = 'f') AS failures
  FROM binaries
  ORDER BY total_checks DESC, uri;
