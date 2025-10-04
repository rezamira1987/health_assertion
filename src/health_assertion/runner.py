"""Main orchestration logic for running health checks."""

from __future__ import annotations

import logging
from typing import List

from tenacity import retry, stop_after_attempt, wait_fixed

from .alerting import send_alerts
from .checks import CheckResult, run_check
from .config import Settings, iter_switches
from .sonic_client import SSHCredentials, sonic_ssh_client

logger = logging.getLogger(__name__)


@retry(wait=wait_fixed(2), stop=stop_after_attempt(3), reraise=True)
def _run_check_with_retry(client, switch: str, check_config) -> CheckResult:
    return run_check(client, switch, check_config)


def run_health_checks(settings: Settings) -> List[CheckResult]:
    """Run health checks for all switches defined in the settings."""

    results: List[CheckResult] = []
    for switch in iter_switches(settings):
        credentials = SSHCredentials(
            host=switch.host,
            username=switch.username,
            password=switch.password,
            port=switch.port,
            timeout=switch.timeout,
        )
        try:
            with sonic_ssh_client(credentials) as client:
                for command in switch.commands:
                    try:
                        result = _run_check_with_retry(client, switch.name, command)
                        results.append(result)
                    except Exception as exc:  # pragma: no cover - defensive logging
                        logger.exception("Check %s on %s failed", command.command, switch.name)
                        results.append(
                            CheckResult(
                                switch=switch.name,
                                description=command.description or command.command,
                                severity=command.severity,
                                success=False,
                                output=str(exc),
                                expectation="Check execution completed without exception",
                            )
                        )
        except Exception as exc:
            logger.exception("Failed to connect to %s", switch.name)
            results.append(
                CheckResult(
                    switch=switch.name,
                    description="Connection failure",
                    severity="critical",
                    success=False,
                    output=str(exc),
                    expectation="SSH connection should succeed",
                )
            )
    send_alerts(settings.alerting, results)
    return results
