import sys
import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph

from agents import (
    budget_agent, final_response_agent, flight_agent,
    hotel_agent, human_approval_agent, itinerary_agent,
    supervisor_agent, weather_agent,
)
from config import DATABASE_URL
from state import TravelState

AGENT_ORDER = ["flight_agent", "hotel_agent", "weather_agent", "budget_agent", "itinerary_agent"]
ROUTE_MAP   = {name: name for name in AGENT_ORDER}


def _ordered_selected(state: TravelState) -> list[str]:
    selected = state.get("selected_agents", [])
    return [a for a in AGENT_ORDER if a in selected]


def route_from_supervisor(state: TravelState) -> str:
    selected = _ordered_selected(state)
    if not selected:
        return END
    return selected[0]


def route_after_agent(current_agent: str):
    def _route(state: TravelState) -> str:
        selected      = _ordered_selected(state)
        current_index = AGENT_ORDER.index(current_agent)
        for next_agent in AGENT_ORDER[current_index + 1:]:
            if next_agent in selected:
                return next_agent
        return "itinerary_agent"
    return _route


def build_graph(checkpointer=None):
    g = StateGraph(TravelState)

    g.add_node("supervisor",      supervisor_agent)
    g.add_node("flight_agent",    flight_agent)
    g.add_node("hotel_agent",     hotel_agent)
    g.add_node("weather_agent",   weather_agent)
    g.add_node("budget_agent",    budget_agent)
    g.add_node("itinerary_agent", itinerary_agent)
    g.add_node("human_approval",  human_approval_agent)
    g.add_node("final_response",  final_response_agent)

    g.add_edge(START, "supervisor")
    g.add_conditional_edges("supervisor", route_from_supervisor, {**ROUTE_MAP, END: END})

    for agent in ["flight_agent", "hotel_agent", "weather_agent", "budget_agent"]:
        g.add_conditional_edges(agent, route_after_agent(agent), ROUTE_MAP)

    g.add_edge("itinerary_agent", "human_approval")
    g.add_edge("human_approval",  "final_response")
    g.add_edge("final_response",  END)

    return g.compile(checkpointer=checkpointer, interrupt_before=["human_approval"])


def _make_checkpointer():
    if not DATABASE_URL:
        print("[graph] No DATABASE_URL set — running without memory.", file=sys.stderr)
        return None
    try:
        conn         = psycopg.connect(DATABASE_URL, autocommit=True)
        checkpointer = PostgresSaver(conn)
        checkpointer.setup()
        print("[graph] Supabase connected.")
        return checkpointer
    except Exception as exc:
        print(f"[graph] DB connection failed: {exc}", file=sys.stderr)
        return None


_checkpointer = _make_checkpointer()
app = build_graph(checkpointer=_checkpointer)
