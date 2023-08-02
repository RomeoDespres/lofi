import os

import dotenv

dotenv.load_dotenv()


def aws_bucket_name() -> str:
    return os.environ["AWS_BUCKET_NAME"]


def db_name() -> str:
    return os.environ["DB_NAME"]
