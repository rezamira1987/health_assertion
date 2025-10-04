"""CLI entrypoint for the health assertion toolkit."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .config import Settings
from .runner import run_health_checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SONiC network health assertion toolkit")
    parser.add_argument("config", type=Path, help="Path to the YAML configuration file")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level))
    settings = Settings.load(args.config)
    run_health_checks(settings)


if __name__ == "__main__":
    main()
