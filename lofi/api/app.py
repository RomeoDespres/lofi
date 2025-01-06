from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI
from pydantic import BaseModel

from . import models

if TYPE_CHECKING:
    from collections.abc import Iterator

    from fastapi.routing import APIRoute


class Route(BaseModel):
    model: type[BaseModel]
    name: str
    path: str


def add_route_to_app(app: FastAPI, route: Route) -> None:
    def generate_unique_id(r: APIRoute) -> str:  # noqa: ARG001
        return route.name

    def fake_route() -> None:
        pass

    app.get(
        route.path,
        generate_unique_id_function=generate_unique_id,
        response_model=route.model,
    )(fake_route)


def build_fastapi_app() -> FastAPI:
    app = FastAPI()
    for route in get_routes():
        add_route_to_app(app, route)
    return app


def get_openapi() -> dict[str, Any]:
    return build_fastapi_app().openapi()


def get_routes() -> Iterator[Route]:
    yield Route(model=models.Labels, name="get_labels", path="./api/labels.json")


def generate_typescript_client(frontend_dir: pathlib.Path) -> None:
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        openapi = get_openapi()
        f.write(json.dumps(openapi))

    subprocess.run(  # noqa: S603
        ["npx", "openapi-typescript-codegen", "--input", f.name, "--output", "src/api"],  # noqa: S607
        cwd=frontend_dir,
        check=False,
    )
    subprocess.run(  # noqa: S603
        ["npx", "prettier", "src", "--write", "--log-level", "silent"],  # noqa: S607
        cwd=frontend_dir,
        check=False,
    )
    pathlib.Path(f.name).unlink()
