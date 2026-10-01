import asyncio
from typing import Any

import httpx

from ..config import get_settings
from ..models import Place, Weather


HEADERS = {
    "User-Agent": "Tripzy-MVP/1.0 (educational project)"
}


async def _get(
    url: str,
    params: dict[str, Any],
) -> Any:
    async with httpx.AsyncClient(
        timeout=get_settings().request_timeout_seconds,
        headers=HEADERS,
    ) as client:
        response = await client.get(
            url,
            params=params,
        )

        response.raise_for_status()

        return response.json()


async def geocode(query: str) -> Place | None:
    try:
        data = await _get(
            "https://nominatim.openstreetmap.org/search",
            {
                "q": query,
                "format": "jsonv2",
                "limit": 1,
            },
        )

        if not data:
            return None

        result = data[0]

        return Place(
            name=result["display_name"].split(",")[0],
            category="destination",
            lat=float(result["lat"]),
            lon=float(result["lon"]),
        )

    except (
        httpx.HTTPError,
        KeyError,
        ValueError,
        TypeError,
    ):
        return None


async def find_places(
    center: Place,
) -> list[Place]:
    query = (
        '[out:json][timeout:10];('
        + "".join(
            f'nwr["{tag}"](around:9000,{center.lat},{center.lon});'
            for tag in [
                "tourism",
                "amenity",
                "leisure",
            ]
        )
        + ");out center 35;"
    )

    try:
        data = await _get(
            "https://overpass-api.de/api/interpreter",
            {"data": query},
        )

        seen: set[str] = set()
        places: list[Place] = []

        for item in data.get("elements", []):
            tags = item.get("tags", {})

            name = tags.get("name")

            coords = (
                item
                if "lat" in item
                else item.get("center", {})
            )

            if (
                not name
                or "lat" not in coords
                or "lon" not in coords
            ):
                continue

            normalized_name = name.lower()

            if normalized_name in seen:
                continue

            category = (
                tags.get("tourism")
                or tags.get("amenity")
                or tags.get("leisure")
                or "place"
            )

            if category in {
                "toilets",
                "bench",
                "parking",
                "waste_basket",
            }:
                continue

            seen.add(normalized_name)

            places.append(
                Place(
                    name=name,
                    category=category.replace("_", " "),
                    lat=float(coords["lat"]),
                    lon=float(coords["lon"]),
                    description=tags.get(
                        "description",
                        "",
                    ),
                )
            )

            if len(places) >= 14:
                break

        return places

    except (
        httpx.HTTPError,
        KeyError,
        ValueError,
        TypeError,
    ):
        return []


async def get_weather(
    center: Place,
) -> Weather:
    try:
        data = await _get(
            "https://api.open-meteo.com/v1/forecast",
            {
                "latitude": center.lat,
                "longitude": center.lon,
                "current": "temperature_2m,weather_code",
                "daily": "precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": 2,
            },
        )

        code = int(
            data["current"]["weather_code"]
        )

        conditions = {
            0: "Clear skies",
            1: "Mostly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Foggy",
            51: "Light drizzle",
            53: "Drizzle",
            55: "Heavy drizzle",
            61: "Rain",
            63: "Rain",
            65: "Heavy rain",
            71: "Snow",
            80: "Rain showers",
            81: "Rain showers",
            82: "Heavy rain showers",
            95: "Thunderstorms",
        }

        rain_values = (
            data.get("daily", {})
            .get(
                "precipitation_probability_max",
                [None],
            )
        )

        rain = rain_values[0] if rain_values else None

        if rain is None or rain < 35:
            tip = "Pack light layers and sunscreen."
        else:
            tip = (
                "Keep a light rain layer and "
                "plan an indoor backup."
            )

        return Weather(
            temperature_c=round(
                data["current"]["temperature_2m"]
            ),
            condition=conditions.get(
                code,
                "Variable conditions",
            ),
            rain_probability=rain,
            tip=tip,
        )

    except (
        httpx.HTTPError,
        KeyError,
        ValueError,
        IndexError,
        TypeError,
    ):
        return Weather()


async def route(
    points: list[Place],
) -> list[list[float]]:
    if len(points) < 2:
        if points:
            return [
                [
                    points[0].lat,
                    points[0].lon,
                ]
            ]

        return []

    coordinates = ";".join(
        f"{place.lon},{place.lat}"
        for place in points
    )

    try:
        data = await _get(
            f"https://router.project-osrm.org/"
            f"route/v1/driving/{coordinates}",
            {
                "overview": "full",
                "geometries": "geojson",
            },
        )

        geometry = (
            data["routes"][0]["geometry"]["coordinates"]
        )

        return [
            [lat, lon]
            for lon, lat in geometry
        ]

    except (
        httpx.HTTPError,
        KeyError,
        ValueError,
        IndexError,
        TypeError,
    ):
        return [
            [place.lat, place.lon]
            for place in points
        ]


async def load_trip_data(
    destination: str,
    starting_location: str | None = None,
):
    center = await geocode(destination)

    if not center:
        raise ValueError(
            f"We couldn't find {destination}. "
            "Try a city, region, or landmark."
        )

    origin = None

    if starting_location:
        origin = await geocode(
            starting_location
        )

    places, weather = await asyncio.gather(
        find_places(center),
        get_weather(center),
    )

    return center, origin, places, weather