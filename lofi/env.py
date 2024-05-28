import os
import pathlib

import dotenv

dotenv.load_dotenv()


def db_name() -> str:
    return os.environ["DB_NAME"]


def local_db() -> pathlib.Path:
    return pathlib.Path(os.environ["LOCAL_DB"])


def new_lofi_playlist_id() -> str:
    return os.environ["NEW_LOFI_PLAYLIST_ID"]


def spotify_user_id() -> str:
    return os.environ["SPOTIFY_USER_ID"]
