from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from ..models import TripPlan
from ..services.planner import build_plan
from .agent import run_tripzy_agent


class TripAgentState(TypedDict, total=False):
    request: str
    destination: str | None
    starting_location: str | None
    travelers: int
    budget: int | None
    interests: list[str]
    start_date: str | None
    end_date: str | None

    agent_response: str

    trip: TripPlan
    notices: list[str]


# ---------------------------------------------------------
# Agent analysis
# ---------------------------------------------------------

async def analyze_request(
    state: TripAgentState,
) -> TripAgentState:

    request = state["request"]

    agent_response = await run_tripzy_agent(
        message=request,
        trip=None
    )

    return {
        "agent_response": agent_response,
    }


# ---------------------------------------------------------
# Generate itinerary
# ---------------------------------------------------------

async def generate_itinerary(
    state: TripAgentState,
) -> TripAgentState:

    trip = await build_plan(
        request=state["request"],
        destination=state.get("destination"),
        starting_location=state.get(
            "starting_location"
        ),
        travelers=state.get("travelers", 2),
        budget=state.get("budget"),
        interests=state.get("interests", []),
        start_date=state.get("start_date"),
        end_date=state.get("end_date"),
    )

    return {
        "trip": trip,
    }


# ---------------------------------------------------------
# Validate itinerary
# ---------------------------------------------------------

def validate_itinerary(
    state: TripAgentState,
) -> TripAgentState:

    trip = state["trip"]

    notices = list(trip.notices)

    if len(trip.itinerary) != trip.days:
        notices.append(
            "The itinerary was shortened while validating the plan."
        )

    if not trip.route:
        notices.append(
            "Route geometry is unavailable; "
            "markers are still shown on the map."
        )

    if not trip.places:
        notices.append(
            "No nearby places were found. "
            "The itinerary is a flexible starter plan."
        )

    return {
        "trip": trip.model_copy(
            update={
                "notices": notices,
            }
        )
    }


# ---------------------------------------------------------
# LangGraph
# ---------------------------------------------------------

workflow = StateGraph(TripAgentState)

workflow.add_node(
    "analyze_request",
    analyze_request,
)

workflow.add_node(
    "generate_itinerary",
    generate_itinerary,
)

workflow.add_node(
    "validate_itinerary",
    validate_itinerary,
)


workflow.add_edge(
    START,
    "analyze_request",
)

workflow.add_edge(
    "analyze_request",
    "generate_itinerary",
)

workflow.add_edge(
    "generate_itinerary",
    "validate_itinerary",
)

workflow.add_edge(
    "validate_itinerary",
    END,
)


trip_agent = workflow.compile()


# ---------------------------------------------------------
# Public runner
# ---------------------------------------------------------

async def run_trip_agent(
    **request: object,
) -> TripPlan:

    result = await trip_agent.ainvoke(
        request
    )

    return result["trip"]