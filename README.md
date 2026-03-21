<p align="center">
  <img src="opguia/static/favicon.svg" width="80" alt="OPGuia icon" />
</p>

<h1 align="center">OPGuia</h1>

<p align="center">
  Dead simple OPC UA browser built with Python.
</p>

<p align="center">
  <a href="https://pypi.org/project/opguia/"><img src="https://img.shields.io/pypi/v/opguia.svg" alt="PyPI" /></a>
  <a href="https://pypi.org/project/opguia/"><img src="https://img.shields.io/pypi/pyversions/opguia.svg" alt="Python" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" /></a>
  <a href="https://pypi.org/project/opguia/"><img src="https://img.shields.io/pypi/dm/opguia.svg" alt="Downloads" /></a>
</p>

---

![Connection page](image.png)
![Browse page](image-2.png)
![Graph view](image-1.png)

## Quick Start

The fastest way to run OPGuia is with [uv](https://docs.astral.sh/uv/):

```bash
uvx opguia
```

> Don't have uv? Install it with `curl -LsSf https://astral.sh/uv/install.sh | sh`
> or see the [uv installation docs](https://docs.astral.sh/uv/getting-started/installation/).

Or install with pip:

```bash
pip install opguia
opguia
```

A native desktop window opens automatically. Enter an OPC UA endpoint or let it auto-discover servers on your network.

## Features

### Browse & Inspect

- Auto-scan for OPC UA servers on standard ports (4840-4843, 48400-48401, 48010, 53530)
- Tree-table view with inline values, types, and status indicators
- Compact 26px rows — scan hundreds of variables at a glance
- Filter nodes by name
- Full node detail dialog with all OPC UA attributes
- Custom struct types resolved and decoded with per-field display
- Copy any attribute value to clipboard

### Write

- Click-to-write for any writable variable with type validation
- Per-index inputs for array types (toggles for booleans, text inputs for numeric/string)
- Integer range checking, float validation, boolean parsing

### Monitor

- Watch panel for live variable tracking
- Live time-series graphs per watched variable (ECharts)
- Configurable poll rate (0.1s to 2.0s)

### Connect

- Connection profiles with per-profile settings (watched vars, tree root, expanded state)
- SSH port-forwarding tunnel support with password or key-based auth
- Live endpoint health pings on saved profiles
- Headless CLI mode for scripting (`opguia --headless`)

### Look & Feel

- Material Dark theme
- Native desktop window via pywebview
- Custom app icon on macOS and Windows

## CLI Mode

Browse, read, and write without the GUI:

```bash
opguia --headless browse opc.tcp://localhost:4840
opguia --headless read  opc.tcp://localhost:4840 "ns=2;s=MyVar"
opguia --headless write opc.tcp://localhost:4840 "ns=2;s=MyVar" 42
opguia --headless tree  opc.tcp://localhost:4840
opguia --headless info  opc.tcp://localhost:4840 "ns=2;s=MyVar"
```

## Development

```bash
git clone https://github.com/KyleAlanJeffrey/opguia
cd opguia
uv sync        # or: python -m venv .venv && pip install -e .
python main.py
```

## Releasing

Releases trigger via GitHub Actions when a commit with title `vX.Y.Z` and body containing `#release` is pushed to `main`.
