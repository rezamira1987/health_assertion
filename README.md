# health_assertion

Toolkit for performing automated health assertions against [SONiC](https://sonic-net.github.io/SONiC/) switches. The tool connects over SSH, runs configurable commands, validates the output against expectations, and emits alerts.

## Features

- YAML-based configuration describing switches and command checks.
- Extensible check types (substring and regular-expression matching).
- Automatic retries for flaky commands.
- Alert destinations including stdout, log files, and Slack webhooks.

## Getting started

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a configuration file similar to [`example_config.yaml`](example_config.yaml) with the switches you want to monitor and the checks to run.

3. Execute the health assertion runner:

   ```bash
   python -m health_assertion path/to/your_config.yaml
   ```

   The command will connect to each switch, execute the configured checks, and emit alerts according to the `alerts` configuration section.

## Configuration reference

Each switch entry supports the following keys:

| Key | Description |
| --- | --- |
| `name` | Friendly name for the switch (used in alerts). |
| `host` | Hostname or IP address of the switch. |
| `username` | SSH username. |
| `password` | SSH password (optional if using key-based auth). |
| `port` | SSH port (default `22`). |
| `timeout` | SSH connection timeout in seconds (default `30`). |
| `checks` | List of command checks to execute. |

Supported check types:

- `command_contains`: checks that the command output contains an expected substring (`expect`).
- `command_regex`: checks that the command output matches a regular expression (`pattern`).

## Alert destinations

Configure alert outputs in the `alerts` block:

- `stdout`: Write alerts to standard output (`true` by default).
- `file`: Append alerts to a log file (directories are created if needed).
- `slack_webhook`: Send alerts to a Slack channel using an incoming webhook URL.

## Extending the tool

The implementation is modular. To add new check types or alert destinations, extend the modules inside `src/health_assertion`.
