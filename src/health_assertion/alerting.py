"""Alerting helpers for the health assertion toolkit."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

import requests

from .checks import CheckResult
from .config import AlertConfig

logger = logging.getLogger(__name__)


def _format_message(result: CheckResult) -> str:
    status = "PASSED" if result.success else "FAILED"
    timestamp = datetime.utcnow().isoformat()
    return (
        f"[{timestamp}] {status} ({result.severity.upper()}) {result.switch}: "
        f"{result.description}\n{result.expectation}\nOutput:\n{result.output.strip()}"
    )


def emit_stdout(results: Iterable[CheckResult]) -> None:
    for result in results:
        print(_format_message(result))


def emit_file(results: Iterable[CheckResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for result in results:
            handle.write(_format_message(result) + "\n")


def emit_slack(results: Iterable[CheckResult], webhook: str) -> None:
    for result in results:
        message = _format_message(result)
        payload = {"text": message}
        response = requests.post(webhook, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        try:
            response.raise_for_status()
        except requests.HTTPError:
            logger.error("Failed to send Slack alert: %s", response.text)


def send_alerts(config: AlertConfig, results: List[CheckResult]) -> None:
    """Dispatch alerts according to the configuration."""

    if config.stdout:
        emit_stdout(results)
    if config.file:
        emit_file(results, config.file)
    if config.slack_webhook:
        emit_slack(results, config.slack_webhook)
