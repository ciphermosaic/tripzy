# Trip Planner Architecture

## 1. System Overview

Trip Planner is a full-stack Agentic AI travel planning application.

The system combines:

* Next.js frontend
* FastAPI backend
* LangGraph agent workflow
* Groq LLM
* External travel data tools
* Supabase PostgreSQL
* Interactive maps
* AI chatbot
* 3D frontend experience

High-level architecture:

```text
                         USER
                           |
                           v
                +---------------------+
                |      Next.js        |
                |      Frontend       |
                +----------+----------+
                           |
                           | HTTP / API
                           v
                +---------------------+
                |       FastAPI       |
                |       Backend       |
                +----------+----------+
                           |
                           v
                +---------------------+
                |      LangGraph      |
                |    Agent Workflow   |
                +----------+----------+
                           |
             +-------------+-------------+
             |                           |
             v                           v
      +-------------+             +---------------+
      |  Groq LLM   |             |     Tools     |
      +-------------+             +---------------+
                                    |    |    |    |
                                    v    v    v    v
                                  OSM  Nominatim OSRM Open-Meteo
                                   
                           |
                           v
                +---------------------+
                |      Supabase       |
                |     PostgreSQL      |
                +---------------------+
```

---

# 2. Frontend Architecture

## Technology

```text
Next.js
React
TypeScript
Tailwind CSS
Motion
React Bits
Three.js
React Three Fiber
Leaflet
```

## Responsibilities

The frontend handles:

* Landing page
* 3D experience
* Trip planning form
* Itinerary display
* Interactive map
* AI chatbot
* Trip modification
* Loading states
* Error states
* Responsive UI

---

# 3. Frontend Structure

Suggested structure:

```text
frontend/
├── app/
│   ├── page.tsx
│   ├── plan/
│   ├── trip/
│   └── api/
│
├── components/
│   ├── ui/
│   ├── landing/
│   ├── planner/
│   ├── itinerary/
│   ├── chatbot/
│   ├── map/
│   └── three/
│
├── lib/
│   ├── api.ts
│   ├── utils.ts
│   └── constants.ts
│
├── hooks/
│
├── types/
│
├── public/
│
└── package.json
```

The exact structure can evolve as the frontend grows.

---

# 4. 3D Architecture

Three.js and React Three Fiber are used for the 3D experience.

```text
React
  |
  v
React Three Fiber
  |
  v
Three.js
  |
  v
WebGL
```

Potential 3D elements:

* Globe
* Terrain
* Destination objects
* Animated routes
* Floating elements
* Background scenes
* Camera animations

3D should be treated as a visual layer.

It should not contain core business logic.

---

# 5. Animation Architecture

Motion and React Bits will handle:

* Page transitions
* Scroll animations
* Element transitions
* Hover interactions
* Loading animations
* Micro-interactions

Three.js handles actual 3D rendering.

The two systems should remain separate where possible.

---

# 6. Map Architecture

Leaflet will handle the interactive map.

```text
Trip Data
    |
    v
Coordinates
    |
    v
Leaflet
    |
    +---- Markers
    |
    +---- Routes
    |
    +---- Day locations
    |
    +---- Selected location
```

Map data comes from the backend.

The frontend should not independently calculate trip routes.

---

# 7. Backend Architecture

## Technology

```text
Python
FastAPI
LangGraph
LangChain
LangChain-Groq
HTTPX
Supabase
```

## Responsibilities

The backend handles:

* API requests
* Input validation
* Agent execution
* Tool execution
* Trip state
* Database operations
* Error handling
* Authentication integration

---

# 8. Backend Structure

Suggested structure:

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── trips.py
│   │   │   └── chat.py
│   │   └── dependencies.py
│   │
│   ├── agents/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── prompts.py
│   │
│   ├── tools/
│   │   ├── places.py
│   │   ├── geocoding.py
│   │   ├── routing.py
│   │   └── weather.py
│   │
│   ├── schemas/
│   │   ├── trip.py
│   │   ├── itinerary.py
│   │   └── chat.py
│   │
│   ├── services/
│   │
│   └── db/
│       ├── client.py
│       └── queries.py
│
├── tests/
├── requirements.txt
├── Dockerfile
└── .env
```

---

# 9. API Layer

FastAPI provides the communication layer between frontend and backend.

Initial endpoints:

```text
POST /api/trips/plan
POST /api/chat
```

Future endpoints:

```text
POST   /api/trips
GET    /api/trips/{trip_id}
PUT    /api/trips/{trip_id}
DELETE /api/trips/{trip_id}

POST   /api/trips/{trip_id}/modify
GET    /api/trips/{trip_id}/messages
```

The API design can evolve during development.

---

# 10. Agent Architecture

The agent is built with LangGraph.

Core architecture:

```text
                    User Request
                         |
                         v
                 Parse Request
                         |
                         v
               Understand Trip
                         |
                         v
                Agent Decision
                         |
             +-----------+-----------+
             |           |           |
             v           v           v
          Places     Routing      Weather
             |           |           |
             +-----------+-----------+
                         |
                         v
                  Process Results
                         |
                         v
                  Build Itinerary
                         |
                         v
                     Validate
                         |
                  +------+------+
                  |             |
                Valid         Invalid
                  |             |
                  v             |
                Output <--------+
```

---

# 11. Agent State

LangGraph will maintain a state object.

Initial conceptual state:

```python
TripState = {
    "user_request": str,

    "destination": str,
    "start_date": str,
    "end_date": str,
    "travelers": int,
    "budget": float,

    "interests": list,
    "travel_style": str,

    "places": list,
    "selected_places": list,
    "routes": list,
    "weather": dict,

    "itinerary": dict,
    "budget_estimate": dict,

    "messages": list,

    "errors": list
}
```

The actual implementation will use a typed state model.

---

# 12. LLM Architecture

The LLM provider is:

**Groq**

The LLM performs:

* Natural language understanding
* Planning
* Reasoning
* Tool selection
* Itinerary generation
* Chatbot responses
* Trip modifications

The LLM does not directly provide authoritative geographic information.

For example:

```text
LLM:
"I need the distance between these two places."

        ↓

Routing Tool:
"Distance = X km"

        ↓

LLM:
Uses the returned value when creating the itinerary.
```

---

# 13. Tool Architecture

Tools are independent backend functions.

## Places Tool

```text
Agent
 ↓
Places Tool
 ↓
Overpass API
 ↓
OpenStreetMap data
 ↓
Structured places
 ↓
Agent
```

## Geocoding Tool

```text
Agent
 ↓
Geocoding Tool
 ↓
Nominatim
 ↓
Coordinates
 ↓
Agent
```

## Routing Tool

```text
Agent
 ↓
Routing Tool
 ↓
OSRM
 ↓
Distance + duration
 ↓
Agent
```

## Weather Tool

```text
Agent
 ↓
Weather Tool
 ↓
Open-Meteo
 ↓
Weather data
 ↓
Agent
```

---

# 14. Tool Design Principles

Every tool should have:

* Clear input schema
* Clear output schema
* Validation
* Timeout
* Error handling
* Rate-limit handling

Tools should be independently testable.

The agent should not need to know how the underlying API works.

For example:

```text
Agent

"Find restaurants near this location."

        ↓

find_places()

        ↓

Overpass API
```

The agent only interacts with the tool interface.

---

# 15. No RAG

The MVP does not use RAG.

There is no:

* Vector database
* Embedding pipeline
* Document ingestion
* ChromaDB
* FAISS
* Pinecone

The system obtains real-world travel information directly from tools.

Architecture:

```text
User
 ↓
Agent
 ↓
Tools
 ↓
Real-world APIs
 ↓
Agent
 ↓
Response
```

Not:

```text
User
 ↓
Agent
 ↓
Vector Database
 ↓
Retrieved Documents
 ↓
Agent
```

---

# 16. Chatbot Architecture

The chatbot is part of the main agent system.

```text
User Message
     |
     v
Chat UI
     |
     v
FastAPI
     |
     v
LangGraph
     |
     +------ Current Trip State
     |
     +------ Conversation History
     |
     +------ Tools
     |
     v
Groq
     |
     v
Response
     |
     v
Chat UI
```

The chatbot can either:

1. Answer a travel question.
2. Modify the current itinerary.

The agent determines which behavior is required.

---

# 17. Trip Modification Architecture

Example:

```text
User:
"Remove the museum from Day 2."

        ↓

Chat API
        ↓
LangGraph
        ↓
Current Trip State
        ↓
Identify modification
        ↓
Update itinerary
        ↓
Recalculate routes if necessary
        ↓
Validate
        ↓
Updated itinerary
```

If the modification requires new information, the agent can call the appropriate tools.

---

# 18. Database Architecture

Database:

**Supabase PostgreSQL**

Initial conceptual schema:

```text
users
  |
  +---- trips
           |
           +---- itineraries
           |
           +---- places
           |
           +---- messages
```

Potential tables:

### users

```text
id
email
created_at
```

### trips

```text
id
user_id
destination
start_date
end_date
travelers
budget
preferences
created_at
updated_at
```

### itineraries

```text
id
trip_id
data
created_at
updated_at
```

### places

```text
id
trip_id
name
latitude
longitude
category
metadata
```

### messages

```text
id
trip_id
role
content
created_at
```

The schema can be changed as implementation requirements become clearer.

---

# 19. Data Flow

Complete trip-planning flow:

```text
User
 ↓
Next.js
 ↓
POST /api/trips/plan
 ↓
FastAPI
 ↓
LangGraph
 ↓
Groq
 ↓
Agent decides tools
 ↓
External APIs
 ↓
Tool results
 ↓
LangGraph
 ↓
Itinerary generation
 ↓
Validation
 ↓
FastAPI
 ↓
Next.js
 ↓
Itinerary + Map
```

---

# 20. Chat Flow

```text
User
 ↓
Chat UI
 ↓
POST /api/chat
 ↓
FastAPI
 ↓
LangGraph
 ↓
Current Trip State
 ↓
Groq
 ↓
Tool calls if necessary
 ↓
Response / Trip modification
 ↓
FastAPI
 ↓
Chat UI
```

---

# 21. Security Architecture

Secrets remain server-side.

Sensitive variables include:

```text
GROQ_API_KEY
SUPABASE_SERVICE_ROLE_KEY
```

These must never be exposed to the browser.

The frontend should communicate with FastAPI.

```text
Browser
   |
   | Public API request
   v
FastAPI
   |
   | Secret API credentials
   v
External Services
```

Not:

```text
Browser
   |
   | Secret API key
   v
External Service
```

---

# 22. Error Handling

External services can fail independently.

Example:

```text
Weather API
     ↓
   FAILURE
     ↓
Agent records error
     ↓
Continue planning
     ↓
Weather marked unavailable
```

The backend should handle:

* Timeouts
* HTTP errors
* Empty responses
* Invalid responses
* Rate limits
* LLM errors
* Tool errors

---

# 23. Caching

Caching is not required for the first prototype.

It can later be added for:

* Popular destinations
* Geocoding
* Places
* Routes
* Weather

Redis can be introduced later if required.

---

# 24. Observability

After the core system works:

```text
User Request
     ↓
FastAPI
     ↓
LangGraph
     ↓
Groq
     ↓
Tools
```

LangSmith can trace:

* Agent runs
* LLM calls
* Tool calls
* Latency
* Errors
* Token usage

This will help debug the agent.

---

# 25. Deployment Architecture

```text
                  INTERNET
                     |
          +----------+----------+
          |                     |
          v                     v
       Vercel                Railway
          |                     |
          |                     |
       Next.js               FastAPI
                                |
                 +--------------+--------------+
                 |              |              |
                 v              v              v
              Groq          Travel APIs     Supabase
                              |              PostgreSQL
                              |
                    +---------+---------+
                    |    |      |       |
                   OSM  OSM    OSRM  Open-Meteo
```

## Deployment Stack

Frontend:

**Vercel**

Backend:

**Railway**

Database:

**Supabase**

Repository:

**GitHub**

Containerization:

**Docker**

CI/CD:

**GitHub Actions**

---

# 26. Cost Architecture

The MVP targets ₹0.

```text
LLM
→ Groq free tier

Places
→ OpenStreetMap / Overpass

Geocoding
→ Nominatim

Routing
→ OSRM

Weather
→ Open-Meteo

Maps
→ Leaflet + OpenStreetMap

Database
→ Supabase free tier

Frontend
→ Vercel

Backend
→ Railway free allowance

Source Control
→ GitHub
```

All services must be used within their applicable free-tier limits and usage policies.

---

# 27. Architecture Principles

## Principle 1

Use the LLM for reasoning, not authoritative real-world facts.

## Principle 2

Use tools for real-world travel information.

## Principle 3

Keep the frontend and backend separated.

## Principle 4

Keep tools independent from the agent.

## Principle 5

Keep the chatbot connected to the current trip state.

## Principle 6

Do not introduce RAG unless a future requirement genuinely needs document-based retrieval.

## Principle 7

Start simple and add complexity only when required.

## Principle 8

Keep the MVP within the ₹0 budget.

## Principle 9

3D should improve the travel experience, not compromise usability or performance.

---

# 28. Final Architecture

```text
                         TRIP PLANNER
                              |
          +-------------------+-------------------+
          |                                       |
          v                                       v
      FRONTEND                                BACKEND
          |                                       |
      Next.js                                  FastAPI
          |                                       |
      React                                      |
          |                                       v
      TypeScript                            LangGraph
          |                                       |
      Tailwind                              +-----+-----+
          |                                  |         |
       Motion                               Groq      Tools
          |                                  |         |
    React Bits                               |    +----+----+----+
          |                                  |    |    |    |    |
   Three.js / R3F                            |   OSM  Nom  OSRM Weather
          |                                  |
      Leaflet                                |
          |                                  |
          +----------------+-----------------+
                           |
                           v
                      Supabase
                      PostgreSQL
```

The core architecture is therefore:

**Next.js → FastAPI → LangGraph → Groq + Tools → Supabase**

with **Leaflet** for maps and **Three.js / React Three Fiber** for the 3D experience.


