import click

import lofi


@click.group
def main() -> None:
    """Main CLI entry point."""
    pass


@main.command
@click.option("--name", help="Label name")
@lofi.db.with_connection
def add_label(session: lofi.db.Session, name: str) -> None:
    """Add label to database."""
    lofi.etl.add_label(session, name)


@main.command
def etl() -> None:
    """Run main ETL."""
    lofi.etl.run()


@main.group
def db() -> None:
    """Database commands."""
    pass


@db.command
def download() -> None:
    """Download database to local file."""
    lofi.db.download_local_db()


@db.command
def upload() -> None:
    """Download database to local file."""
    lofi.db.upload_local_db()
