from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from core.settings import postgres_settings


async def ensure_celery_database():
    engine = create_async_engine(
        postgres_settings.async_app_database_url,
        echo=False,
        isolation_level="AUTOCOMMIT",
    )

    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": postgres_settings.celery_db},
            )
            exists = result.scalar() is not None

            if not exists:
                await conn.execute(
                    text(f'CREATE DATABASE "{postgres_settings.celery_db}"')
                )
    finally:
        await engine.dispose()
