"""Configuration parsing utilities for the health assertion toolkit."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import yaml


@dataclass
class CommandCheckConfig:
    """Configuration required to execute a command based assertion."""

    type: str
    command: str
    expect: Optional[str] = None
    pattern: Optional[str] = None
    severity: str = "warning"
    description: Optional[str] = None

    def validate(self) -> None:
        if self.type not in {"command_contains", "command_regex"}:
            raise ValueError(f"Unsupported check type: {self.type}")
        if self.type == "command_contains" and not self.expect:
            raise ValueError("command_contains check requires 'expect'")
        if self.type == "command_regex" and not self.pattern:
            raise ValueError("command_regex check requires 'pattern'")


@dataclass
class SwitchConfig:
    """Connection information for a SONiC switch and its checks."""

    name: str
    host: str
    username: str
    password: Optional[str] = None
    port: int = 22
    timeout: int = 30
    commands: List[CommandCheckConfig] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "SwitchConfig":
        commands = [CommandCheckConfig(**cmd) for cmd in data.get("checks", [])]
        for command in commands:
            command.validate()
        return cls(
            name=data["name"],
            host=data["host"],
            username=data["username"],
            password=data.get("password"),
            port=data.get("port", 22),
            timeout=data.get("timeout", 30),
            commands=commands,
        )


@dataclass
class AlertConfig:
    """Settings controlling how alerts are emitted."""

    stdout: bool = True
    file: Optional[Path] = None
    slack_webhook: Optional[str] = None


@dataclass
class Settings:
    """Top level configuration describing switches and alerting destinations."""

    switches: List[SwitchConfig]
    alerting: AlertConfig

    @classmethod
    def load(cls, path: Path) -> "Settings":
        data = yaml.safe_load(path.read_text())
        if not data:
            raise ValueError("Configuration file is empty")
        switches = [SwitchConfig.from_dict(item) for item in data.get("switches", [])]
        if not switches:
            raise ValueError("No switches defined in configuration")
        alert_data = data.get("alerts", {})
        alerting = AlertConfig(
            stdout=alert_data.get("stdout", True),
            file=Path(alert_data["file"]) if alert_data.get("file") else None,
            slack_webhook=alert_data.get("slack_webhook"),
        )
        return cls(switches=switches, alerting=alerting)


def iter_switches(settings: Settings) -> Iterable[SwitchConfig]:
    """Helper to iterate switches in the configuration."""

    yield from settings.switches
