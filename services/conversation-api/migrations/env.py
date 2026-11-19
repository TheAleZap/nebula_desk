"""Alembic entry point: runs migrations against DATABASE_URL (injected by app/db.py).

Applied migrations are recorded in the schema_migrations table, so each runs once.
Offline mode (alembic upgrade head --sql) prints the SQL without touching a database.
"""

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
VERSION_TABLE = "schema_migrations"

if context.is_offline_mode():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        literal_binds=True,
        version_table=VERSION_TABLE,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, version_table=VERSION_TABLE)
        with context.begin_transaction():
            context.run_migrations()
