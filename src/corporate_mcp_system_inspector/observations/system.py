"""Operating-system and runtime identity observations."""

import platform
import socket
import sys

from ..models import SERVER_ID
from .. import __version__


def collect_identity() -> dict[str, str]:
    return {
        "operating_system": platform.system(),
        "platform": platform.platform(aliased=True),
        "architecture": platform.machine(),
        "hostname": socket.gethostname(),
        "python_version": sys.version.split()[0],
        "server_id": SERVER_ID,
        "server_version": __version__,
    }
