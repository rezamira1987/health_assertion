"""Assertion checks run against SONiC switches."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Callable, Optional

from .config import CommandCheckConfig
from .sonic_client import run_command

logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Result of executing a single check."""

    switch: str
    description: str
    severity: str
    success: bool
    output: str
    expectation: str


CheckExecutor = Callable[[CommandCheckConfig, str], CheckResult]


def execute_command_contains(config: CommandCheckConfig, output: str, switch: str) -> CheckResult:
    success = config.expect in output
    expectation = f"Expected substring '{config.expect}'"
    return CheckResult(
        switch=switch,
        description=config.description or f"Command '{config.command}' contains substring",
        severity=config.severity,
        success=success,
        output=output,
        expectation=expectation,
    )


def execute_command_regex(config: CommandCheckConfig, output: str, switch: str) -> CheckResult:
    pattern = re.compile(config.pattern or "")
    match = pattern.search(output)
    expectation = f"Expected pattern '{config.pattern}'"
    return CheckResult(
        switch=switch,
        description=config.description or f"Command '{config.command}' matches regex",
        severity=config.severity,
        success=bool(match),
        output=output,
        expectation=expectation,
    )


EXECUTORS: dict[str, Callable[[CommandCheckConfig, str, str], CheckResult]] = {
    "command_contains": execute_command_contains,
    "command_regex": execute_command_regex,
}


def run_check(client, switch: str, config: CommandCheckConfig) -> CheckResult:
    """Run an individual check on the given SSH client."""

    logger.info("Running check '%s' on %s", config.description or config.command, switch)
    output = run_command(client, config.command)
    executor = EXECUTORS[config.type]
    return executor(config, output, switch)
