# fixitydb-prototype

This is a prototype application to implement a fixity checks database for 
fcrepo using a PostgreSQL database and the [PostgREST](https://docs.postgrest.org/)
API layer.

## Quick Start

Uses Python 3.14:

```zsh
pyenv install 3.14.0
```

Close, setup Python environment, and install:

```zsh
git clone git@github.com:peichman-umd/fixitydb-prototype.git
cd fixitydb-prototype
python -mvenv .venv --prompt "fixitydb-prototype-py3.14"
source .venv/bin/activate
pip install -e .
```

Create a `.env`:

```zsh
SECRET=$(uuidgen | tr -d '-')
echo "PGRST_JWT_SECRET=$SECRET" >> .env
echo "FIXITYDB_ENDPOINT=http://localhost:3333" >> .env
echo "FIXITYDB_TOKEN=$(python mktoken.py fixity $SECRET)" >> .env
```

Start up the Docker compose:

```zsh
docker compose up -d
```

### REST API endpoints

(defined in [01-tables.sql](docker-entrypoint-initdb.d/01-tables.sql)):

* List of all binaries: <http://localhost:3333/binaries>
* List of all fixity check results: <http://localhost:3333/results>
* Least recently checked resources: <http://localhost:3333/least_recent>
* Stats about the checks: <http://localhost:3333/stats>

Load 1000 fcrepo-qa URIs and last modified dates:

```zsh
python load_uris.py qa-uris.csv
```

Run a fixity check of the 100 least recently checked resources:

```zsh
python check_least_recent.py 100
```
