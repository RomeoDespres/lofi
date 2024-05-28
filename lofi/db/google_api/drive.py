from __future__ import annotations

import socket
from typing import TYPE_CHECKING, LiteralString

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .credentials import get_google_credentials

if TYPE_CHECKING:
    import pathlib

    from googleapiclient._apis.drive.v3 import DriveResource


class GoogleDriveFileNotFoundError(Exception):
    def __init__(self, file_name: str) -> None:
        msg = f"File with name {file_name} does not exist"
        super().__init__(msg)


class MultipleGoogleDriveFileError(Exception):
    def __init__(self, file_name: str, n: int) -> None:
        msg = f"{n} files exist with name {file_name}"
        super().__init__(msg)


def download_file(drive: DriveResource, drive_file_name: str, local_file: pathlib.Path) -> None:
    file_id = get_file_id(drive, drive_file_name)
    content = drive.files().get_media(fileId=file_id).execute()
    local_file.write_bytes(content)


def get_file_id(drive: DriveResource, file_name: str, *, create_if_missing: bool = False) -> str:
    q = f"name = '{file_name}' and trashed = false"
    search_results = drive.files().list(q=q).execute()
    n_files = len(search_results["files"])
    if n_files == 0:
        if not create_if_missing:
            raise GoogleDriveFileNotFoundError(file_name)
        drive.files().create(body={"name": file_name}, uploadType="media").execute()
        return get_file_id(drive, file_name, create_if_missing=False)
    if n_files > 1:
        raise MultipleGoogleDriveFileError(file_name, n_files)
    return search_results["files"][0]["id"]


def get_google_drive_client() -> DriveResource:
    default_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(60 * 15)
    client = build("drive", "v3", credentials=get_google_credentials(["https://www.googleapis.com/auth/drive.file"]))
    socket.setdefaulttimeout(default_timeout)
    return client


def upload_file(drive: DriveResource, drive_file_name: LiteralString, local_file: pathlib.Path) -> None:
    file_id = get_file_id(drive, drive_file_name, create_if_missing=True)
    drive.files().update(fileId=file_id, media_body=MediaFileUpload(local_file), uploadType="resumable").execute()
