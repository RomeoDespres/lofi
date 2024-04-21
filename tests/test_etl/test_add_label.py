import pytest

import lofi.etl.main
from lofi import db
from lofi.etl.errors import LabelAlreadyExistsError
from lofi.etl.main import add_label
from lofi.spotify_api import Playlist
from tests.utils import LabelGenerator, PlaylistGenerator, load_data_output

from .conftest import get_spotify_api_client_patch


@pytest.fixture()
@load_data_output
def playlist(session: db.Session, playlist_generator: PlaylistGenerator) -> db.Playlist:  # noqa: ARG001
    return playlist_generator.generate()


@pytest.fixture()
@load_data_output
def label(session: db.Session, playlist: db.Playlist, label_generator: LabelGenerator) -> db.Label:  # noqa: ARG001
    return label_generator.generate(playlist=playlist)


@pytest.fixture()
def _patch_spotify_api_client(
    session: db.Session,
    monkeypatch: pytest.MonkeyPatch,
    playlist_generator: PlaylistGenerator,
) -> None:
    def create_playlist(name: str, *args: object, **kwargs: object) -> Playlist:  # noqa: ARG001
        return Playlist.model_validate(
            {
                "id": (playlist_id := playlist_generator.generate().id),
                "images": [],
                "name": name,
                "owner": {
                    "id": f"Owner ID of playlist {playlist_id}",
                    "display_name": f"Owner name of playlist {playlist_id}",
                },
                "snapshot_id": "",
            },
        )

    api_client_patch = get_spotify_api_client_patch(session, create_playlist=create_playlist)
    monkeypatch.setattr(lofi.etl.main, "SpotifyAPIClient", api_client_patch)


@pytest.mark.usefixtures("_patch_spotify_api_client")
def test_add_label_with_existing_label_raises_error(session: db.Session, label: db.Label) -> None:
    with pytest.raises(LabelAlreadyExistsError):
        add_label(session, label.name)


@pytest.mark.usefixtures("_patch_spotify_api_client")
def test_add_label(session: db.Session, label_generator: LabelGenerator) -> None:
    label = label_generator.generate()
    assert session.get(db.Label, label.name) is None
    add_label(session, label.name)
    assert session.get(db.Label, label.name) is not None
