# shared/db/alembic/env.py
import apps.api.models_olympiad  # noqa: F401
import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# make sure project root is on PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import our settings and models
from shared.settings import settings  # noqa: E402
from sqlmodel import SQLModel
# Import modules that define models so metadata is populated
# Ensure any module that has SQLModel table models is imported here:
# from apps.api import models_olympiad  # <-- uncomment/add your model modules
# If you keep models in several files, import them all here:
try:
    # lazy import: import package where models live
    import apps.api.models_olympiad  # noqa: F401
except Exception:
    # won't fail here if module missing; but best to import real models
    pass

target_metadata = SQLModel.metadata

# Provide DB URL from settings (preferred) or fallback to alembic.ini
def get_url():
    # settings.DATABASE_URL expects env file or env variable
    db_url = getattr(settings, "DATABASE_URL", None)
    if not db_url:
        # fallback to sqlalchemy.url in alembic.ini
        db_url = config.get_main_option("sqlalchemy.url")
    return db_url

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=get_url(),
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
