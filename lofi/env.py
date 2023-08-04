import os
import pathlib

import dotenv


dotenv.load_dotenv()


def aws_bucket_name() -> str:
    return os.environ["AWS_BUCKET_NAME"]


def db_name() -> str:
    return os.environ["DB_NAME"]


def spotify_user_id() -> str:
    return os.environ["SPOTIFY_USER_ID"]


def local_db() -> pathlib.Path:
    return pathlib.Path(os.environ["LOCAL_DB"])
