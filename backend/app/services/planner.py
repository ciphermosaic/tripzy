import re
import uuid
from datetime import date

from groq import Groq

from ..config import get_settings
from ..models import (
    BudgetEstimate,
    DayPlan,
    ItineraryItem,
    Place,
    TripPlan,
)
from .travel_data import (
    load_trip_data,
    route,
)

settings = get_settings()

client = (
    Groq(api_key=settings.groq_api_key)
    if settings.groq_api_key
    else None
)


def parse_budget(text: str) -> int | None:
    text = text.lower().replace(",", "")

    patterns = [
        r"(?:₹|rs\.?|inr)\s*(\d+(?:\.\d+)?)\s*k\b",
        r"(\d+(?:\.\d+)?)\s*k\s*(?:₹|rs\.?|inr)?",
        r"(?:₹|rs\.?|inr)\s*(\d+(?:\.\d+)?)",
        r"budget\s*(?:of|is|:)?\s*(\d+(?:\.\d+)?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if not match:
            continue

        value = float(match.group(1))

        if "k" in match.group(0):
            value *= 1000

        return int(value)

    return None






def _interest_matches(
    place: Place,
    interests: list[str],
) -> bool:
    if not interests:
        return True

    text = (
        f"{place.name} "
        f"{place.category} "
        f"{place.description}"
    ).lower()

    return any(
        interest.lower() in text
        for interest in interests
    )


def _select_places(
    places: list[Place],
    days: int,
    interests: list[str],
) -> list[Place]:
    if not places:
        return []

    preferred = [
        place
        for place in places
        if _interest_matches(
            place,
            interests,
        )
    ]

    pool = preferred + [
        place
        for place in places
        if place not in preferred
    ]

    return pool[: max(2, days * 2)]

KNOWN_DESTINATIONS = [
    "Goa",
    "Kerala",
    "Jaipur",
    "Udaipur",
    "Manali",
    "Mumbai",
    "Delhi",
    "Bengaluru",
    "Hyderabad",
    "Kolkata",
    "Chennai",
    "Pondicherry",
    "Rishikesh",
    "Varanasi",
    "Darjeeling",
    "Kochi",
    "Munnar",
]

def infer_destination(
    request: str,
    destination: str | None,
) -> str | None:
    if destination:
        return destination.strip()

    text = request.lower()

    for known_destination in KNOWN_DESTINATIONS:
        if known_destination.lower() in text:
            return known_destination

    return None


def infer_days(
    text: str,
    start: str | None,
    end: str | None,
) -> int:
    if start and end:
        try:
            return max(
                1,
                min(
                    14,
                    (
                        date.fromisoformat(end)
                        - date.fromisoformat(start)
                    ).days
                    + 1,
                ),
            )
        except ValueError:
            pass

    match = re.search(
        r"(\d+)\s*(?:day|days|night|nights)",
        text,
        re.I,
    )

    return (
        max(1, min(10, int(match.group(1))))
        if match
        else 3
    )





def budget_estimate(
    total: int,
    days: int,
) -> BudgetEstimate:
    parts = {
        "accommodation": round(total * 0.38),
        "food": round(total * 0.22),
        "transport": round(total * 0.16),
        "activities": round(total * 0.14),
    }

    parts["miscellaneous"] = (
        total - sum(parts.values())
    )

    return BudgetEstimate(
        **parts,
        total=total,
        note=(
            f"Per-person estimate for {days} days. "
            "Accommodation is a mid-range shared-stay "
            "assumption; actual costs vary by season."
        ),
    )


async def build_plan(
    request: str,
    destination: str | None,
    starting_location: str | None,
    travelers: int,
    budget: int | None,
    interests: list[str],
    start_date: str | None,
    end_date: str | None,
) -> TripPlan:

    destination = infer_destination(
        request,
        destination,
    )

    if not destination:
        raise ValueError(
            "Tell us where you want to go - "
            "for example, 'Plan 4 days in Goa'."
        )

    days = infer_days(
        request,
        start_date,
        end_date,
    )

    parsed_budget = parse_budget(request)
    total_budget = budget if budget is not None else (parsed_budget or 18000)

    center, origin, found_places, weather = await load_trip_data(
        destination,
        starting_location,
    )

    selected = (
        found_places or [center]
    )[: max(3, days * 2)]

    itinerary = []

    all_stops = []

    if origin:
        all_stops.append(origin)

    all_stops.append(center)

    for index in range(days):
        first = selected[
            (index * 2) % len(selected)
        ]

        second = (
            selected[
                (index * 2 + 1) % len(selected)
            ]
            if len(selected) > 1
            else center
        )

        all_stops.extend([
            first,
            second,
        ])

        item_cost = max(
            100,
            total_budget // (days * 18),
        )

        itinerary.append(
            DayPlan(
                day=index + 1,
                title=(
                    "Arrival & orientation"
                    if index == 0
                    else f"A local day in {destination}"
                ),
                summary=(
                    "Outdoor-first plan."
                    if not weather.rain_probability
                    or weather.rain_probability < 35
                    else
                    "Have an indoor alternative ready "
                    "if showers arrive."
                ),
                items=[
                    ItineraryItem(
                        time="09:00",
                        title=f"Start near {first.name}",
                        description=(
                            "Begin unhurriedly; confirm "
                            "local hours before leaving."
                        ),
                        duration="1 hr",
                        place=first,
                    ),
                    ItineraryItem(
                        time="11:00",
                        title=f"Explore {first.name}",
                        description=(
                            f"A {first.category} stop selected "
                            "from nearby OpenStreetMap places."
                        ),
                        duration="2 hrs",
                        estimated_cost=item_cost,
                        place=first,
                    ),
                    ItineraryItem(
                        time="14:00",
                        title="Lunch & local break",
                        kind="food",
                        description=(
                            "Choose a well-reviewed local "
                            "spot nearby and take a proper pause."
                        ),
                        duration="1.5 hrs",
                        estimated_cost=max(
                            200,
                            total_budget // (days * 12),
                        ),
                    ),
                    ItineraryItem(
                        time="16:30",
                        title=f"Discover {second.name}",
                        description=(
                            f"Make time for this "
                            f"{second.category} before the "
                            "evening slows down."
                        ),
                        duration="2 hrs",
                        estimated_cost=item_cost,
                        place=second,
                    ),
                    ItineraryItem(
                        time="19:30",
                        title="Free evening",
                        kind="food",
                        description=(
                            "Dinner, a sunset walk, or "
                            "downtime - keep this intentionally flexible."
                        ),
                        duration="2 hrs",
                        estimated_cost=max(
                            200,
                            total_budget // (days * 10),
                        ),
                    ),
                ],
            )
        )

    notices = [
        "Places and weather use live public data when available."
    ]

    if origin is None and starting_location:
        notices.append(
            f"Could not locate '{starting_location}', "
            "so the route starts from the destination."
        )

    if not found_places:
        notices.append(
            "Nearby place results were unavailable, "
            "so this is a flexible starter itinerary."
        )

    route_points = all_stops[:10]

    return TripPlan(
        id=str(uuid.uuid4()),
        destination=destination,
        starting_location=starting_location,
        origin=origin,
        center=center,
        travelers=travelers,
        days=days,
        itinerary=itinerary,
        weather=weather,
        budget=budget_estimate(
            total_budget,
            days,
        ),
        places=selected,
        route=await route(route_points),
        notices=notices,
    )

def apply_trip_modification(
    message: str,
    trip: TripPlan,
):
    lowered = message.lower()

    if any(
        word in lowered
        for word in [
            "cheaper",
            "cheap",
            "save money",
            "lower budget",
        ]
    ):
        new_total = round(
            trip.budget.total * 0.85
        )

        updated_days = []

        for day in trip.itinerary:
            new_items = []

            for item in day.items:
                new_items.append(
                    item.model_copy(
                        update={
                            "estimated_cost": round(
                                item.estimated_cost
                                * 0.85
                            )
                        }
                    )
                )

            updated_days.append(
                day.model_copy(
                    update={
                        "items": new_items
                    }
                )
            )

        updated_trip = trip.model_copy(
            update={
                "itinerary": updated_days,
                "budget": budget_estimate(
                    new_total,
                    trip.days,
                ),
                "notices": [
                    *trip.notices,
                    "Budget reduced by approximately 15%.",
                ],
            }
        )

        return (
            updated_trip,
            "I reduced the estimated trip budget by about 15%.",
        )

    if any(
        word in lowered
        for word in [
            "relaxed",
            "less travel",
            "slow",
            "slower",
        ]
    ):
        updated_days = []

        for day in trip.itinerary:
            activity_items = [
                item
                for item in day.items
                if item.kind == "activity"
            ]

            if len(activity_items) > 1:
                remove_item = activity_items[-1]

                items = [
                    item
                    for item in day.items
                    if item is not remove_item
                ]
            else:
                items = day.items

            updated_days.append(
                day.model_copy(
                    update={
                        "items": items
                    }
                )
            )

        updated_trip = trip.model_copy(
            update={
                "itinerary": updated_days,
                "notices": [
                    *trip.notices,
                    "Itinerary pace was reduced.",
                ],
            }
        )

        return (
            updated_trip,
            "I made the itinerary more relaxed.",
        )

    if "remove" in lowered:
        updated_days = []

        for day in trip.itinerary:
            activity_items = [
                item
                for item in day.items
                if item.kind == "activity"
            ]

            if activity_items:
                remove_item = activity_items[-1]

                items = [
                    item
                    for item in day.items
                    if item is not remove_item
                ]

                updated_days.append(
                    day.model_copy(
                        update={
                            "items": items
                        }
                    )
                )
            else:
                updated_days.append(day)

        updated_trip = trip.model_copy(
            update={
                "itinerary": updated_days
            }
        )

        return (
            updated_trip,
            "I removed an activity from the itinerary.",
        )

    return None, ""


def chat_reply(
    message: str,
    trip: TripPlan,
) -> str:
    if client:
        try:
            response = client.chat.completions.create(
                model=settings.groq_model,
                temperature=0.3,
                max_tokens=250,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Tripzy's travel assistant. "
                            "Answer using only the supplied trip "
                            "information. Do not invent exact "
                            "prices, weather, routes or places."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Trip: {trip.model_dump_json()}\n\n"
                            f"User: {message}"
                        ),
                    },
                ],
            )

            return (
                response.choices[0]
                .message.content
                .strip()
            )

        except Exception as error:
            print("CHAT LLM ERROR:", repr(error))

    lowered = message.lower()

    if "weather" in lowered:
        return (
            f"The current forecast for {trip.destination} "
            f"is {trip.weather.condition} at around "
            f"{trip.weather.temperature_c}°C."
        )

    if "pack" in lowered:
        return trip.weather.tip

    if "budget" in lowered:
        return (
            f"The current estimated budget is "
            f"₹{trip.budget.total:,} per person."
        )

    return (
        f"Your {trip.days}-day trip to "
        f"{trip.destination} is ready. "
        "You can ask me to make it cheaper, "
        "more relaxed, or remove an activity."
    )