import asyncio
import click
import uvicorn
import subprocess
import sys
from pathlib import Path
import logging
from core.logging import setup_logging
from core.sentry import init_sentry
from core.settings import celery_settings
from core.utils import ensure_celery_database


@click.group()
def cli():
    """Backend CLI"""
    init_sentry()
    setup_logging()


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--workers", default=1, help="Number of worker processes")
def serve(host, port, reload, workers):
    """Start the API server"""

    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
    )


@cli.command()
def celery_worker():
    """Run the celery worker"""
    asyncio.run(ensure_celery_database())
    subprocess.run(
        [
            "celery",
            "-A",
            "domain.celery_app",
            "worker",
            f"--concurrency={celery_settings.concurrency}",
            "--loglevel=info",
        ],
        check=True,
    )


@cli.command()
def flower():
    """Run the flower server"""
    subprocess.run(
        [
            "celery",
            "-A",
            "domain.celery_app",
            "flower",
            f"--port={celery_settings.flower_port}",
        ],
        check=True,
    )


@cli.command()
def upgrade_database():
    """Upgrade the database to the latest version"""
    logging.info("Upgrading database to the latest version")
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=str(Path(__file__).parent / "repository"),
        check=True,
    )
    logging.info("Database upgraded successfully!")


@cli.command()
@click.option("--message", "-m", required=True, help="Migration message")
def generate_migration(message: str):
    """Generate a new database migration"""
    logging.info(f"Generating migration: {message}")

    cmd = [sys.executable, "-m", "alembic", "revision", "-m", message, "--autogenerate"]

    subprocess.run(cmd, cwd=str(Path(__file__).parent / "repository"), check=True)

    logging.info("Migration generated successfully!")


@cli.command()
@click.option("--revision", default="head", help="Revision to upgrade to")
def downgrade(revision: str):
    """Downgrade the database to the specified revision"""
    logging.info(f"Downgrading database to revision: {revision}")
    subprocess.run(
        ["alembic", "downgrade", revision],
        cwd=str(Path(__file__).parent / "repository"),
        check=True,
    )
    logging.info("Database downgraded successfully!")


if __name__ == "__main__":
    cli()
