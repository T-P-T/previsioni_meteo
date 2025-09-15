import argparse
import csv
import datetime
import os
import unicodedata
from typing import Dict, List, Tuple

import pycountry
import requests


def get_provinces() -> List[str]:
    """Return the list of Italian province and metropolitan city names."""
    provinces = []
    for subdiv in pycountry.subdivisions.get(country_code="IT"):
        if subdiv.type in {"Province", "Metropolitan city"}:
            provinces.append(subdiv.name)
    return sorted(provinces)


PROVINCE_ALIASES = {
    "Barletta-Andria-Trani": "Barletta",
    "Forlì-Cesena": "Forli",
    "Massa-Carrara": "Massa",
    "Monza e Brianza": "Monza",
    "Pesaro e Urbino": "Pesaro",
    "Sud Sardegna": "Carbonia",
    "Verbano-Cusio-Ossola": "Verbania",
}


def geocode(name: str) -> Tuple[float, float]:
    """Return latitude and longitude of a province using Open-Meteo geocoding."""
    queries = [PROVINCE_ALIASES.get(name, name)]
    base = queries[0]
    simplified = base.replace("-", " ").split()[0]
    if simplified.lower() != base.lower():
        queries.append(simplified)

    for query in queries:
        normalized = unicodedata.normalize("NFKD", query).encode("ascii", "ignore").decode("ascii")
        resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": normalized, "country": "IT", "count": 1, "language": "it"},
            timeout=10,
        )
        data = resp.json()
        if "results" in data and data["results"]:
            first = data["results"][0]
            return first["latitude"], first["longitude"]
    raise ValueError(f"Coordinate non trovate per {name}")


def fetch_forecast(lat: float, lon: float, days: int = 5) -> Dict:
    """Fetch hourly temperature forecast for given coordinates."""
    resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m",
            "forecast_days": days,
            "timezone": "Europe/Rome",
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["hourly"]


def main(limit: int | None) -> None:
    provinces = get_provinces()
    if limit:
        provinces = provinces[:limit]

    times: List[str] | None = None
    rows: List[Tuple[str, List[float]]] = []
    for name in provinces:
        try:
            lat, lon = geocode(name)
            forecast = fetch_forecast(lat, lon)
            if times is None:
                times = forecast["time"]
            rows.append((name, forecast["temperature_2m"]))
            print(f"Raccolte previsioni per {name}")
        except Exception as exc:
            print(f"Errore per {name}: {exc}")

    if not rows:
        print("Nessuna previsione raccolta")
        return

    os.makedirs("data", exist_ok=True)
    filename = f"data/previsioni_{datetime.date.today().isoformat()}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["provincia"] + (times or []))
        for province, temps in rows:
            writer.writerow([province] + temps)
    print(f"Salvati dati in {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scarica previsioni meteo provinciali")
    parser.add_argument(
        "--limit",
        type=int,
        help="Elabora solo le prime N province (per test)",
    )
    args = parser.parse_args()
    main(args.limit)
