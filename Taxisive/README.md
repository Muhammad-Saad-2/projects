# Taxisive

## PostgreSQL

The API uses PostgreSQL through SQLAlchemy's asyncpg driver. Configure
`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, and `DB_PASSWORD` in the environment
or a `.env` file. Start with `.env.example` as a template, and set
`DB_HOST=postgres` when using Docker Compose. On startup, the app verifies the
connection and creates the `charges` table if it does not exist. If PostgreSQL
is unavailable, database endpoints respond with HTTP 503.

To run the local Docker stack:

```sh
docker compose -f Docker/compose.yaml up --build
```