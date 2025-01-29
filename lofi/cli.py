import pathlib
import subprocess

import click

import lofi
from lofi.db.google_api import get_google_drive_client
from lofi.db.google_api.credentials import DEFAULT_API_TOKEN_PATH


@click.group
def main() -> None:
    """Run main CLI entry point."""


@main.command
@click.option("--name", help="Label name")
@lofi.db.with_connection
def add_label(session: lofi.db.Session, name: str) -> None:
    """Add label to database."""
    lofi.etl.add_label(session, name)


@main.command
@click.option("--label", help="Label name")
@click.option("--playlist-id", help="Playlist ID")
@lofi.db.with_connection
def add_label_playlist(session: lofi.db.Session, label: str, playlist_id: str) -> None:
    """Add label to database."""
    db_label = session.get(lofi.db.Label, label)
    assert db_label is not None

    if playlist_id in {p.id for p in db_label.filtering_playlists}:
        return

    session.add(lofi.db.Playlist(id=playlist_id, is_editorial=False, filter_for_label_name=label))


@main.command
def etl() -> None:
    """Run main ETL."""
    lofi.etl.run()


@main.group
def db() -> None:
    """Database commands."""


@db.command
def auth() -> None:
    """Regenerate Google API token to reach database."""
    DEFAULT_API_TOKEN_PATH.unlink(missing_ok=True)
    get_google_drive_client()
    subprocess.run(  # noqa: S603
        ["gh", "secret", "set", "GOOGLE_API_TOKEN", "--body", DEFAULT_API_TOKEN_PATH.read_text()],  # noqa: S607
        check=False,
    )


@db.command
def download() -> None:
    """Download database to local file."""
    lofi.db.download_local_db()


@db.command
def upload() -> None:
    """Download database to local file."""
    lofi.db.upload_local_db()


@main.group
def frontend() -> None:
    """Frontend commands."""


@frontend.command
@click.argument("frontend-dir", type=click.Path(exists=True), default="frontend")
def generate_api_client(frontend_dir: str) -> None:
    """Generate TypeScript API client."""
    import lofi.api

    lofi.api.generate_typescript_client(pathlib.Path(frontend_dir))


@frontend.command
@click.argument("frontend-dir", type=click.Path(exists=True), default="frontend")
def generate_data(frontend_dir: str) -> None:
    """Generate data files in public folder."""
    import lofi.api

    lofi.api.generate_data(pathlib.Path(frontend_dir))
