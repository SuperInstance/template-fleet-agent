# Fleet Weather Agent ☀️🌧️❄️

A skeleton weather agent for fleet deployment. Fetches weather data
from [wttr.in](https://wttr.in) (no API key required).

## Quick Start

```bash
pip install -r requirements.txt
python3 agent.py --help
python3 agent.py fetch --city "San Francisco"
python3 agent.py monitor --city Tokyo --interval 30 --count 10
```

## Commands

- `fetch` — Get current weather for a city
- `monitor` — Poll weather at regular intervals

## CI / Build

```bash
python3 -m pip install -r requirements.txt
python3 -m py_compile agent.py
python3 agent.py --help
```
