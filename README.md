# GoBeyond — Multi-Agent AI Travel Planner

A multi-agent travel planning system built with LangGraph. You describe a trip, and eight agents work through it together — pulling real flight data, hotel options, and weather info before handing you a complete day-by-day plan that you review before it's finalized.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1.2+-FF6B35?style=flat)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45+-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat&logo=supabase&logoColor=white)

---

## How it works

```mermaid
flowchart TD
    A([Your travel request]) --> B[Supervisor]

    B -->|Not a travel request| Z([Blocked])

    B --> C[Flight Agent]
    C --> D[Hotel Agent]
    D --> E[Weather Agent]
    E --> F[Budget Agent]
    F --> G[Itinerary Agent]

    G --> H{You review the draft}

    H -->|Looks good| I[Final Response Agent]
    H -->|Make changes| I

    I --> J([Final travel plan])

    style B fill:#1a3a5c,color:#fff,stroke:#3a7bd5
    style H fill:#7c3a00,color:#fff,stroke:#f59e0b
    style I fill:#003a1a,color:#fff,stroke:#10b981
    style Z fill:#3a0000,color:#fff,stroke:#ef4444
```

The supervisor first checks if the request makes sense. If it does, it figures out which agents are needed and passes the job along. Each agent adds its piece — flights, hotels, weather, budget — and the itinerary agent puts it all together into a draft. You then review that draft, approve it or give feedback, and the final agent writes up the finished plan.

Conversation history is stored in Supabase PostgreSQL so your session continues even if you close the tab.

---

## Agent breakdown

| Agent | What it does |
|-------|-------------|
| Supervisor | Validates the request, picks which agents to run, extracts trip details |
| Flight Agent | Queries AviationStack for airport and airline data, generates flight guidance |
| Hotel Agent | Searches hotels and neighbourhoods via Tavily web search |
| Weather Agent | Gets current weather and a 5-day forecast from OpenWeatherMap |
| Budget Agent | Checks whether the plan fits the budget and flags any risks |
| Itinerary Agent | Puts everything together into a day-by-day travel plan |
| Human Approval | Pauses and waits for you to approve or revise the draft |
| Final Response | Writes the polished final plan based on your decision |

---

## Data flow

```mermaid
sequenceDiagram
    participant U as You
    participant S as Supervisor
    participant F as Flight Agent
    participant H as Hotel Agent
    participant W as Weather Agent
    participant B as Budget Agent
    participant I as Itinerary Agent
    participant DB as Supabase

    U->>S: Travel request
    S->>DB: Save checkpoint
    S->>F: Trip constraints
    F->>DB: Save checkpoint
    F->>H: Pass state
    H->>DB: Save checkpoint
    H->>W: Pass state
    W->>DB: Save checkpoint
    W->>B: Pass state
    B->>DB: Save checkpoint
    B->>I: Pass state
    I->>U: Draft itinerary
    U->>I: Approve or revise
    I->>U: Final plan
```

---

## Tech stack

| Layer | Tech |
|-------|------|
| Agent framework | LangGraph |
| LLM | Groq — LLaMA 3.3 70B |
| Memory | Supabase PostgreSQL |
| Web search | Tavily MCP |
| Flight data | AviationStack MCP |
| Weather | OpenWeatherMap MCP |
| Frontend | Streamlit |

---

## Project structure

```
gobeyond/
├── config.py               env vars and LLM setup
├── state.py                shared state definition
├── agents.py               all eight agent functions
├── graph.py                graph wiring and Supabase checkpointer
├── mcp_client.py           connects to Tavily, AviationStack, and weather MCP
├── mcp_weather_server.py   local weather MCP server
├── main.py                 CLI entry point
├── frontend.py             Streamlit app
├── tools/
│   ├── flight_tool.py      direct AviationStack REST helper
│   └── tavily_tool.py      direct Tavily search helper
├── .env.example            env template
└── requirements.txt
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YadavAkhileshh/GoBeyond.git
cd GoBeyond
```

### 2. Create and activate a virtual environment

```bash
python -m venv langgraph_env
langgraph_env\Scripts\activate       # Windows
source langgraph_env/bin/activate    # macOS / Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your `.env`

```bash
cp .env.example .env
```

Fill in your keys. The app needs Groq, Tavily, AviationStack, OpenWeatherMap, and a Supabase database URL.

### 5. Set up Supabase

Create a project at [supabase.com](https://supabase.com), then go to **Settings → Database → Connection string** and copy the Transaction pooler URL (port 6543). Paste it as `DATABASE_URL` in your `.env`. LangGraph creates the tables on first run.

### 6. Set up the AviationStack MCP server

```bash
git clone https://github.com/Pradumnasaraf/aviationstack-mcp.git
cd aviationstack-mcp
pip install uv
uv sync
cd ..
```

---

## Run

```bash
streamlit run frontend.py
```

Or from the terminal:

```bash
python main.py
python main.py --query "7-day Japan trip under 2 lakhs"
```

---

## API keys you need

| Service | Link |
|---------|------|
| Groq | https://console.groq.com |
| Tavily | https://tavily.com |
| AviationStack | https://aviationstack.com |
| OpenWeatherMap | https://openweathermap.org/api |
| Supabase | https://supabase.com |

---

## License

MIT
