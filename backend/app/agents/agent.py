import json

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from tavily import TavilyClient

from ..config import get_settings
from ..models import TripPlan


settings = get_settings()


# =========================================================
# Tavily
# =========================================================

tavily = (
    TavilyClient(api_key=settings.tavily_api_key)
    if settings.tavily_api_key
    else None
)


# =========================================================
# Tavily travel search tool
# =========================================================

@tool
def search_travel_places(
    destination: str,
    category: str,
) -> str:
    """
    Search the web for real travel places.

    Use this when the user asks for a specific type of
    place such as beaches, restaurants, attractions,
    viewpoints, temples, nightlife, shopping, etc.
    """

    if not tavily:
        return "Tavily search is unavailable."

    query = (
        f"best {category} places to visit in "
        f"{destination}"
    )

    try:
        response = tavily.search(
            query=query,
            search_depth="basic",
            max_results=8,
            include_answer=True,
        )

        results = response.get("results", [])

        if not results:
            return (
                f"No useful {category} places were found "
                f"for {destination}."
            )

        formatted_results = []

        for index, result in enumerate(
            results,
            start=1,
        ):
            formatted_results.append(
                f"{index}. {result.get('title', '')}\n"
                f"Description: {result.get('content', '')}\n"
                f"Source: {result.get('url', '')}"
            )

        return "\n\n".join(formatted_results)

    except Exception as error:
        print(
            "TAVILY TOOL ERROR:",
            repr(error),
        )

        return (
            "Tavily search failed. "
            "Use the information already available "
            "in the trip data."
        )


# =========================================================
# Groq
# =========================================================

llm = ChatGroq(
    api_key=settings.groq_api_key,
    model=settings.groq_model,
    temperature=0,
)


# =========================================================
# Tripzy Agent
# =========================================================

tripzy_agent = create_agent(
    model=llm,
    tools=[
        search_travel_places,
    ],
    system_prompt="""
You are Tripzy's travel assistant.

You help users create and modify travel itineraries.

You have access to:
1. The user's current TripPlan.
2. A Tavily travel search tool.

IMPORTANT:

When the user asks to modify the current itinerary,
actually determine what needs to change.

Examples:

"Add a beach on day 3"
"Replace St. Rita's Church with a beach"
"Add a restaurant on day 2"
"Remove the church from day 3"

For requests requiring a new place:

1. Identify the destination.
2. Identify the requested place category.
3. Search Tavily.
4. Select a suitable real place from the results.
5. Return a structured modification.

Your final response MUST be JSON.

For a modification, return:

{
  "changed": true,
  "message": "short explanation",
  "day": 3,
  "action": "replace",
  "old_activity": "St. Rita's Church",
  "new_place": {
    "name": "Beach name",
    "category": "beach",
    "description": "short description"
  }
}

If the user is only asking a question and does not want
to modify the itinerary, return:

{
  "changed": false,
  "message": "answer to the user"
}

Do not invent places.
Use Tavily when a requested place is not available
in the current TripPlan.
""",
)


# =========================================================
# Run the agent
# =========================================================

async def run_tripzy_agent(
    message: str,
    trip: TripPlan | None = None,
) -> dict:

    trip_context = (
    trip.model_dump_json(indent=2)
    if trip is not None
    else "No existing trip. This is a new trip request."
)

    prompt = f"""
    CURRENT TRIP:

    {trip_context}

    USER REQUEST:

    {message}

    Analyze the user's request.

    If there is an existing trip and the user wants to
    modify it, determine the required modification.

    If this is a new trip request, do not try to modify
    an existing itinerary.

    If a new place is required, use the Tavily search tool.
    
    Return ONLY the JSON structure requested by your
    system instructions.
    """

    result = await tripzy_agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        }
    )

    messages = result.get(
        "messages",
        [],
    )

    if not messages:
        return {
            "changed": False,
            "message": "I couldn't generate a response.",
        }

    final_message = messages[-1]

    content = getattr(
        final_message,
        "content",
        None,
    )

    if not content:
        return {
            "changed": False,
            "message": "I couldn't generate a response.",
        }

    content = str(content).strip()

    # Remove accidental markdown JSON fences.
    if content.startswith("```"):
        content = content.replace(
            "```json",
            "",
        )
        content = content.replace(
            "```",
            "",
        )
        content = content.strip()

    try:
        return json.loads(content)

    except json.JSONDecodeError:
        return {
            "changed": False,
            "message": content,
        }