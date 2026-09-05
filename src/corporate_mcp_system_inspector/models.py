"""Typed response models for the observation-only server."""

from dataclasses import asdict, dataclass
from typing import Any

from . import __version__

SERVER_ID = "corporate.system-inspector"


@dataclass(frozen=True)
class ErrorDetail:
    code: str
    message: str


@dataclass(frozen=True)
class SuccessEnvelope:
    ok: bool
    server_id: str
    server_version: str
    observation: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ErrorEnvelope:
    ok: bool
    server_id: str
    server_version: str
    error: ErrorDetail

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def success(observation: dict[str, Any]) -> dict[str, Any]:
    return SuccessEnvelope(True, SERVER_ID, __version__, observation).to_dict()


def failure(code: str, message: str) -> dict[str, Any]:
    return ErrorEnvelope(False, SERVER_ID, __version__, ErrorDetail(code, message)).to_dict()
