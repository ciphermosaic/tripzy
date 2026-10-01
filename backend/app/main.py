from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models import (
    ChatRequest,
    ChatResponse,
    PlanRequest,
    TripPlan,
)
from .agents.graph import run_trip_agent
from .agents.agent import run_tripzy_agent
from .services.planner import (
    apply_trip_modification,
    chat_reply,
)
from .database import supabase


settings = get_settings()


app = FastAPI(
    title="Tripzy API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "llm_configured": bool(
            settings.groq_api_key
        ),
        "tavily_configured": bool(
            settings.tavily_api_key
        ),
    }


def get_user_id(
    authorization: str | None,
) -> str:

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header",
        )

    token = authorization.replace(
        "Bearer ",
        "",
        1,
    )

    try:
        response = supabase.auth.get_user(
            token
        )

        user = response.user

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token",
            )

        return user.id

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )


# =========================================================
# PLAN TRIP
# =========================================================

@app.post("/api/trips/plan")
async def plan_trip(
    payload: PlanRequest,
    authorization: str | None = Header(
        default=None
    ),
):

    try:
        user_id = get_user_id(
            authorization
        )

        trip = await run_trip_agent(
            request=payload.request,
            destination=payload.destination,
            starting_location=payload.starting_location,
            travelers=payload.travelers,
            budget=payload.budget,
            interests=payload.interests,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )

        supabase.table("trips").insert(
            {
                "user_id": user_id,
                "destination": trip.destination,
                "days": trip.days,
                "travelers": trip.travelers,
                "trip_data": trip.model_dump(),
            }
        ).execute()

        return trip

    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error),
        ) from error

    except HTTPException:
        raise

    except Exception as error:
        print(
            "TRIP ERROR:",
            repr(error),
        )

        raise HTTPException(
            status_code=503,
            detail=str(error),
        )


# =========================================================
# APPLY AGENT MODIFICATION
# =========================================================

def apply_agent_change(
    trip: TripPlan,
    agent_result: dict,
) -> tuple[TripPlan | None, str]:

    if not agent_result.get("changed"):
        return (
            None,
            agent_result.get(
                "message",
                "I couldn't find a change to make.",
            ),
        )

    day_number = agent_result.get("day")

    action = agent_result.get(
        "action",
        "replace",
    )

    old_activity = agent_result.get(
        "old_activity"
    )

    new_place = agent_result.get(
        "new_place"
    )

    if not isinstance(day_number, int):
        return (
            None,
            "I couldn't determine which day to modify.",
        )

    if day_number < 1 or day_number > trip.days:
        return (
            None,
            f"Day {day_number} does not exist in this trip.",
        )

    if not isinstance(new_place, dict):
        return (
            None,
            "I couldn't find a suitable new place.",
        )

    day_index = day_number - 1

    day = trip.itinerary[day_index]

    items = list(day.items)

    # Find the activity requested by the agent.
    target_index = None

    if old_activity:
        old_lower = str(
            old_activity
        ).lower()

        for index, item in enumerate(items):
            if (
                old_lower in item.title.lower()
                or old_lower in item.description.lower()
            ):
                target_index = index
                break

    # If no exact activity was found,
    # replace the last activity item.
    if target_index is None:

        activity_indices = [
            index
            for index, item in enumerate(items)
            if item.kind == "activity"
        ]

        if activity_indices:
            target_index = activity_indices[-1]

    if target_index is None:
        return (
            None,
            "I couldn't find an activity to replace.",
        )

    place_name = str(
        new_place.get(
            "name",
            "New place",
        )
    )

    category = str(
        new_place.get(
            "category",
            "activity",
        )
    )

    description = str(
        new_place.get(
            "description",
            "",
        )
    )

    # -----------------------------------------------------
    # Replace existing activity
    # -----------------------------------------------------

    if action == "replace":

        old_item = items[target_index]

        items[target_index] = old_item.model_copy(
            update={
                "title": f"Explore {place_name}",
                "description": (
                    description
                    or f"Visit {place_name}, "
                    f"a {category} in {trip.destination}."
                ),
                "kind": "activity",
            }
        )

    # -----------------------------------------------------
    # Add new activity
    # -----------------------------------------------------

    elif action == "add":

        from .models import ItineraryItem

        items.append(
            ItineraryItem(
                time="16:30",
                title=f"Explore {place_name}",
                kind="activity",
                description=(
                    description
                    or f"Visit {place_name}, "
                    f"a {category} in {trip.destination}."
                ),
                duration="2 hrs",
                estimated_cost=0,
            )
        )

    else:
        return (
            None,
            f"I don't know how to perform '{action}'.",
        )

    updated_day = day.model_copy(
        update={
            "items": items,
        }
    )

    updated_itinerary = list(
        trip.itinerary
    )

    updated_itinerary[day_index] = updated_day

    updated_trip = trip.model_copy(
        update={
            "itinerary": updated_itinerary,
            "notices": [
                *trip.notices,
                (
                    f"Day {day_number} was updated "
                    f"with {place_name}."
                ),
            ],
        }
    )

    return (
        updated_trip,
        agent_result.get(
            "message",
            f"I updated Day {day_number}.",
        ),
    )


# =========================================================
# CHAT
# =========================================================

@app.post(
    "/api/chat",
    response_model=ChatResponse,
)
async def chat(
    payload: ChatRequest,
    authorization: str | None = Header(
        default=None
    ),
):

    get_user_id(
        authorization
    )

    try:

        # ---------------------------------------------
        # Let the AI agent understand the request
        # ---------------------------------------------

        agent_result = await run_tripzy_agent(
            message=payload.message,
            trip=payload.trip,
        )

        # ---------------------------------------------
        # Agent wants to modify itinerary
        # ---------------------------------------------

        updated_trip, change_message = (
            apply_agent_change(
                payload.trip,
                agent_result,
            )
        )

        if updated_trip is not None:

            return ChatResponse(
                message=change_message,
                trip=updated_trip,
                changed=True,
            )

        # ---------------------------------------------
        # Existing deterministic modifications
        # remain as fallback
        # ---------------------------------------------

        fallback_trip, fallback_message = (
            apply_trip_modification(
                payload.message,
                payload.trip,
            )
        )

        if fallback_trip is not None:

            return ChatResponse(
                message=fallback_message,
                trip=fallback_trip,
                changed=True,
            )

        # ---------------------------------------------
        # Normal conversational response
        # ---------------------------------------------

        message = agent_result.get(
            "message"
        )

        if not message:
            message = chat_reply(
                payload.message,
                payload.trip,
            )

        return ChatResponse(
            message=message,
            trip=None,
            changed=False,
        )

    except Exception as error:

        print(
            "CHAT AGENT ERROR:",
            repr(error),
        )

        # Keep the old chat system as a fallback
        # if the agent fails.

        fallback_trip, fallback_message = (
            apply_trip_modification(
                payload.message,
                payload.trip,
            )
        )

        if fallback_trip is not None:

            return ChatResponse(
                message=fallback_message,
                trip=fallback_trip,
                changed=True,
            )

        return ChatResponse(
            message=chat_reply(
                payload.message,
                payload.trip,
            ),
            trip=None,
            changed=False,
        )