from app.models import (
    BudgetEstimate,
    DayPlan,
    ItineraryItem,
    Place,
    TripPlan,
    Weather,
)
from app.services.planner import apply_trip_modification


def make_trip() -> TripPlan:
    place = Place(name="Museum", category="museum", lat=1, lon=2)
    return TripPlan(
        id="test", destination="Goa", center=place, travelers=2, days=1,
        itinerary=[DayPlan(day=1, title="Day one", summary="Busy", items=[
            ItineraryItem(time="10:00", title="Explore Museum", description="Visit", duration="2 hrs", estimated_cost=1000, place=place),
            ItineraryItem(time="14:00", title="Lunch", kind="food", description="Eat", duration="1 hr", estimated_cost=500),
        ])],
        weather=Weather(),
        budget=BudgetEstimate(accommodation=4000, food=2000, transport=1000, activities=2000, miscellaneous=1000, total=10000, note="Estimate"),
        places=[place], route=[[1, 2]], notices=[],
    )


def test_remove_activity_from_day():
    trip, response = apply_trip_modification("Remove the museum from Day 1", make_trip())
    assert trip is not None
    assert response == "I removed an activity from the itinerary."
    assert len(trip.itinerary[0].items) == 1


def test_make_trip_cheaper():
    trip, _ = apply_trip_modification("Make this trip cheaper", make_trip())
    assert trip is not None
    assert trip.budget.total == 8500
