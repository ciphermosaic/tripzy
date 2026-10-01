from typing import Literal
from pydantic import BaseModel, Field


class PlanRequest(BaseModel):
    request: str = Field(min_length=3, max_length=1200)
    destination: str | None = Field(default=None, max_length=120)
    starting_location: str | None = Field(default=None, max_length=120)
    start_date: str | None = None
    end_date: str | None = None
    travelers: int = Field(default=2, ge=1, le=20)
    budget: int | None = Field(default=None, ge=1000, le=2_000_000)
    interests: list[str] = Field(default_factory=list, max_length=8)
    travel_style: str | None = None


class Place(BaseModel):
    name: str
    category: str
    lat: float
    lon: float
    description: str = ""


class ItineraryItem(BaseModel):
    time: str
    title: str
    kind: Literal["activity", "food", "travel", "stay"] = "activity"
    description: str
    duration: str
    estimated_cost: int = 0
    place: Place | None = None


class DayPlan(BaseModel):
    day: int
    title: str
    summary: str
    items: list[ItineraryItem]


class Weather(BaseModel):
    temperature_c: float | None = None
    condition: str = "Weather unavailable"
    rain_probability: int | None = None
    tip: str = "Check the forecast closer to departure."


class BudgetEstimate(BaseModel):
    accommodation: int
    food: int
    transport: int
    activities: int
    miscellaneous: int
    total: int
    note: str


class TripPlan(BaseModel):
    id: str
    destination: str
    starting_location: str | None = None
    origin: Place | None = None
    center: Place
    travelers: int
    days: int
    itinerary: list[DayPlan]
    weather: Weather
    budget: BudgetEstimate
    places: list[Place]
    route: list[list[float]] = Field(default_factory=list)
    notices: list[str] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    trip: TripPlan


class ChatResponse(BaseModel):
    message: str
    trip: TripPlan | None = None
    changed: bool = False