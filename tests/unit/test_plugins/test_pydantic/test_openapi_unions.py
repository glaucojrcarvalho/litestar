"""Regressions for OpenAPI union validation semantics (issue #5131)."""

from enum import StrEnum

from pydantic import BaseModel

from litestar import Litestar, get


class Status(StrEnum):
    RUNNING = "running"
    DONE = "done"


class Run(BaseModel):
    status: Status | str


class OptionalRun(BaseModel):
    status: Status | str | None


def test_pydantic_overlapping_union_emits_any_of() -> None:
    @get("/run")
    async def get_run() -> Run:
        return Run(status=Status.RUNNING)

    spec = Litestar([get_run]).openapi_schema.to_schema()
    schema = spec["components"]["schemas"]["Run"]["properties"]["status"]

    assert schema == {
        "anyOf": [
            {"$ref": "#/components/schemas/Status"},
            {"type": "string"},
        ]
    }


def test_pydantic_optional_overlapping_union_emits_any_of() -> None:
    @get("/run")
    async def get_run() -> OptionalRun:
        return OptionalRun(status=Status.RUNNING)

    spec = Litestar([get_run]).openapi_schema.to_schema()
    schema = spec["components"]["schemas"]["OptionalRun"]["properties"]["status"]

    assert schema == {
        "anyOf": [
            {"$ref": "#/components/schemas/Status"},
            {"type": "string"},
            {"type": "null"},
        ]
    }
