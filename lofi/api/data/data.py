import pathlib
from typing import Iterator

from pydantic import BaseModel

from lofi import db

from .labels import get_labels


class Datum(BaseModel):
    path: str
    obj: BaseModel


def generate_data(frontend_dir: pathlib.Path) -> None:
    with db.connect() as session:
        for datum in get_data(session):
            write_datum(frontend_dir, datum)


def get_data(session: db.Session) -> Iterator[Datum]:
    yield Datum(path="labels.json", obj=get_labels(session))


def write_datum(frontend_dir: pathlib.Path, d: Datum) -> None:
    p = frontend_dir / "public" / "api" / d.path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(d.obj.model_dump_json(by_alias=True), encoding="utf8")
