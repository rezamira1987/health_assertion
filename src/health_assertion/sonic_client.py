"""SSH client helpers for interacting with SONiC switches."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Optional

import paramiko

logger = logging.getLogger(__name__)


@dataclass
class SSHCredentials:
    """Credentials used to connect to a SONiC device."""

    host: str
    username: str
    password: Optional[str]
    port: int = 22
    timeout: int = 30


@contextmanager
def sonic_ssh_client(credentials: SSHCredentials) -> Iterator[paramiko.SSHClient]:
    """Context manager that yields a connected SSH client."""

    logger.debug("Connecting to %s:%s", credentials.host, credentials.port)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            credentials.host,
            port=credentials.port,
            username=credentials.username,
            password=credentials.password,
            timeout=credentials.timeout,
        )
        logger.debug("Connected to %s", credentials.host)
        yield client
    finally:
        logger.debug("Closing SSH connection to %s", credentials.host)
        client.close()


def run_command(client: paramiko.SSHClient, command: str, timeout: Optional[int] = None) -> str:
    """Execute a command on the SSH client and return its output."""

    logger.debug("Executing command: %s", command)
    stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
    output = stdout.read().decode("utf-8")
    error = stderr.read().decode("utf-8")
    if error:
        logger.debug("Command produced stderr: %s", error.strip())
    logger.debug("Command output: %s", output.strip())
    return output
