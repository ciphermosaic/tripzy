# Trippsz

**AI-powered travel planning made simple.**

Trippsz is an AI-powered trip planner that helps users create personalized travel itineraries using natural language. It combines AI planning, interactive maps, budget breakdowns, authentication, and a conversational travel assistant into a single web application.

🌐 **Live Website:** https://trippsz.vercel/app

---

## 🚀 Features

- 🤖 **AI Trip Planner**  
  Generate personalized travel plans based on destination, duration, budget, interests, and preferences.

- 🗺️ **Interactive Itinerary & Maps**  
  Visualize destinations and planned locations using interactive maps.

- 💬 **AI Travel Assistant**  
  Chat with an AI assistant to ask questions, modify plans, and get travel suggestions.

- 💰 **Budget Breakdown**  
  View estimated expenses and understand how your trip budget is distributed.

- 🌍 **Interactive 3D Globe**  
  Explore destinations through an interactive WebGL-based globe.

- 🔐 **User Authentication**  
  Secure authentication and user sessions powered by Supabase.

- ⚡ **Modern Web Experience**  
  Responsive interface built with React, TypeScript, Tailwind CSS, and modern animation libraries.

---

## 🛠️ Tech Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Three.js
- React Three Fiber
- Leaflet
- Motion

### Backend
- FastAPI
- Python
- REST APIs

### AI
- Groq API
- LLM-powered trip planning
- Conversational AI

### Database & Authentication
- Supabase
- PostgreSQL

### Deployment
- Vercel
- Render
- Docker

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │      User           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │  TypeScript + Vite  │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐       ┌─────────────────┐
        │  FastAPI Backend │       │    Supabase     │
        │                  │       │ Auth + Database │
        └────────┬────────┘       └─────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │    Groq LLM     │
        │  AI Trip Planner│
        └─────────────────┘
```

---

## 📂 Project Structure

```text
trippsz/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── GlobeScene.tsx
│   │   ├── TripMap.tsx
│   │   ├── TravelCard.tsx
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── services/
│   ├── planner.py
│   ├── travel_data.py
│   ├── models.py
│   ├── config.py
│   ├── database.py
│   └── main.py
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/trippsz.git
cd trippsz
```

### 2. Configure environment variables

Create `.env` files for the frontend and backend and add the required API credentials.

Example:

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The application will then be available locally through the development server.

---

## 🐳 Docker

Trippsz can also be containerized using Docker.

Build the Docker image:

```bash
docker build -t trippsz .
```

Run the container:

```bash
docker run -p 8000:8000 trippsz
```

---

## 🔑 Environment Variables

The following environment variables may be required depending on the deployment configuration:

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API authentication key |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase public anonymous key |
| `GROQ_MODEL` | LLM used for AI trip planning |

**Never commit API keys or secrets to GitHub.**

---

## 🎯 Use Cases

Trippsz can be used to:

- Generate complete travel itineraries
- Plan trips based on a specific budget
- Discover places to visit
- Organize destinations and activities
- Ask travel-related questions through AI chat
- Visualize travel routes and destinations
- Modify travel plans conversationally

---

## 📸 Demo

🌐 **Try Trippsz:**  
https://trippsz.vercel/app

---

## 🔮 Future Improvements

- Hotel and flight integrations
- Real-time weather information
- Live travel pricing
- More detailed expense tracking
- Saved and shareable itineraries
- Multi-destination trip optimization
- Personalized recommendations based on previous trips
- Mobile application

---

## 👨‍💻 Author

**Abu Bakar**

AI/ML Developer | Generative AI | Agentic AI

GitHub: https://github.com/ciphermosaic

LinkedIn: https://www.linkedin.com/in/abubakar-35aa3a316/

---

## 📄 License

This project is developed as a personal project for learning, experimentation, and portfolio purposes.# ✈️ Trippsz

**AI-powered travel planning made simple.**

Trippsz is an AI-powered trip planner that helps users create personalized travel itineraries using natural language. It combines AI planning, interactive maps, budget breakdowns, authentication, and a conversational travel assistant into a single web application.

🌐 **Live Website:** https://trippsz.vercel/app

---

## 🚀 Features

- 🤖 **AI Trip Planner**  
  Generate personalized travel plans based on destination, duration, budget, interests, and preferences.

- 🗺️ **Interactive Itinerary & Maps**  
  Visualize destinations and planned locations using interactive maps.

- 💬 **AI Travel Assistant**  
  Chat with an AI assistant to ask questions, modify plans, and get travel suggestions.

- 💰 **Budget Breakdown**  
  View estimated expenses and understand how your trip budget is distributed.

- 🌍 **Interactive 3D Globe**  
  Explore destinations through an interactive WebGL-based globe.

- 🔐 **User Authentication**  
  Secure authentication and user sessions powered by Supabase.

- ⚡ **Modern Web Experience**  
  Responsive interface built with React, TypeScript, Tailwind CSS, and modern animation libraries.

---

## 🛠️ Tech Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Three.js
- React Three Fiber
- Leaflet
- Motion

### Backend
- FastAPI
- Python
- REST APIs

### AI
- Groq API
- LLM-powered trip planning
- Conversational AI

### Database & Authentication
- Supabase
- PostgreSQL

### Deployment
- Vercel
- Render
- Docker

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │      User           │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │  TypeScript + Vite  │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐       ┌─────────────────┐
        │  FastAPI Backend │       │    Supabase     │
        │                  │       │ Auth + Database │
        └────────┬────────┘       └─────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │    Groq LLM     │
        │  AI Trip Planner│
        └─────────────────┘
```

---

## 📂 Project Structure

```text
trippsz/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── GlobeScene.tsx
│   │   ├── TripMap.tsx
│   │   ├── TravelCard.tsx
│   │   └── ...
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── services/
│   ├── planner.py
│   ├── travel_data.py
│   ├── models.py
│   ├── config.py
│   ├── database.py
│   └── main.py
│
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/trippsz.git
cd trippsz
```

### 2. Configure environment variables

Create `.env` files for the frontend and backend and add the required API credentials.

Example:

```env
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

### 3. Start the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The application will then be available locally through the development server.

---

## 🐳 Docker

Trippsz can also be containerized using Docker.

Build the Docker image:

```bash
docker build -t trippsz .
```

Run the container:

```bash
docker run -p 8000:8000 trippsz
```

---

## 🔑 Environment Variables

The following environment variables may be required depending on the deployment configuration:

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API authentication key |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_ANON_KEY` | Supabase public anonymous key |
| `GROQ_MODEL` | LLM used for AI trip planning |

**Never commit API keys or secrets to GitHub.**

---

## 🎯 Use Cases

Trippsz can be used to:

- Generate complete travel itineraries
- Plan trips based on a specific budget
- Discover places to visit
- Organize destinations and activities
- Ask travel-related questions through AI chat
- Visualize travel routes and destinations
- Modify travel plans conversationally

---

## 📸 Demo

🌐 **Try Trippsz:**  
https://trippsz.vercel/app

---

## 🔮 Future Improvements

- Hotel and flight integrations
- Real-time weather information
- Live travel pricing
- More detailed expense tracking
- Saved and shareable itineraries
- Multi-destination trip optimization
- Personalized recommendations based on previous trips
- Mobile application

---

## 👨‍💻 Author

**Abu Bakar**

AI/ML Developer | Generative AI | Agentic AI

GitHub: https://github.com/ciphermosaic

---

## 📄 License

This project is developed as a personal project for learning, experimentation, and portfolio purposes.
