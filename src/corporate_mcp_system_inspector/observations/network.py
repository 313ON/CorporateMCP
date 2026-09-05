"""Bounded local network observations; no scanning or host probing."""

import socket
from typing import Any


def collect_network_summary() -> dict[str, Any]:
    hostname = socket.gethostname()
    addresses: set[str] = set()
    try:
        for result in socket.getaddrinfo(hostname, None, type=socket.SOCK_DGRAM):
            address = result[4][0]
            if not address.startswith(("127.", "::1")):
                addresses.add(address)
    except socket.gaierror:
        pass

    try:
        interfaces = [{"name": name, "operational_state": "unknown", "addresses": []} for _, name in socket.if_nameindex()]
    except (AttributeError, OSError):
        interfaces = []
    if addresses and interfaces:
        interfaces[0]["addresses"] = sorted(addresses)
    return {"hostname": hostname, "interfaces": interfaces}
