#!/usr/bin/env python3
"""
fleet-weather-agent — skeleton weather agent for fleet deployment.

Usage:
    python3 agent.py --help
    python3 agent.py fetch --city "San Francisco"
    python3 agent.py monitor --interval 60
"""

import sys
import json
import time
import logging
from typing import Optional

import click
import httpx
from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler

# ─── Logging ───────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, handlers=[RichHandler()])
log = logging.getLogger("weather-agent")
console = Console()

# ─── Weather API (wttr.in — no API key needed) ────────────────────────
WTTR_BASE = "https://wttr.in"

def fetch_weather(city: str, format: str = "json") -> dict:
    """Fetch weather for a city using wttr.in."""
    url = f"{WTTR_BASE}/{city}"
    params = {"format": format}
    log.info("Fetching weather for %s …", city)
    resp = httpx.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def display_weather(data: dict, city: str) -> None:
    """Render weather data as a rich table."""
    try:
        current = data.get("current_condition", [{}])[0]
        table = Table(title=f"Weather: {city}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        temp_c = current.get("temp_C", "?")
        feels_c = current.get("FeelsLikeC", "?")
        humidity = current.get("humidity", "?")
        desc = current.get("weatherDesc", [{}])[0].get("value", "?")
        wind_speed = current.get("windspeedKmph", "?")
        wind_dir = current.get("winddir16Point", "?")

        table.add_row("Temperature", f"{temp_c}°C")
        table.add_row("Feels Like", f"{feels_c}°C")
        table.add_row("Condition", desc)
        table.add_row("Humidity", f"{humidity}%")
        table.add_row("Wind", f"{wind_speed} km/h {wind_dir}")

        console.print(table)
    except (KeyError, IndexError, TypeError) as exc:
        log.error("Failed to parse weather data: %s", exc)
        console.print(json.dumps(data, indent=2))


# ─── CLI ───────────────────────────────────────────────────────────────
@click.group()
@click.version_option("0.1.0")
def cli():
    """Weather agent for fleet deployment."""


@cli.command()
@click.option("--city", default="London", help="City to fetch weather for")
@click.option("--json-output", is_flag=True, help="Output raw JSON")
def fetch(city: str, json_output: bool):
    """Fetch and display current weather for a city."""
    try:
        data = fetch_weather(city)
    except httpx.HTTPStatusError as exc:
        log.error("HTTP error: %s", exc)
        sys.exit(1)
    except httpx.RequestError as exc:
        log.error("Network error: %s", exc)
        sys.exit(1)

    if json_output:
        console.print(json.dumps(data, indent=2))
    else:
        display_weather(data, city)


@cli.command()
@click.option("--city", default="London", help="City to monitor")
@click.option("--interval", default=60, type=int, help="Poll interval in seconds")
@click.option("--count", default=5, type=int, help="Number of polls")
def monitor(city: str, interval: int, count: int):
    """Continuously monitor weather for a city."""
    log.info("Monitoring %s every %ds (%d polls) …", city, interval, count)
    for i in range(count):
        try:
            data = fetch_weather(city)
            display_weather(data, city)
            if i < count - 1:
                time.sleep(interval)
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            log.error("Poll %d failed: %s", i + 1, exc)
            time.sleep(interval)  # wait and retry


if __name__ == "__main__":
    cli()
