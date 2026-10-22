import asyncio
import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import interrupt

from config import get_llm
from mcp_client import current_weather, forecast, list_airlines, list_airports, tavily_search
from state import TravelState

llm = get_llm()


def _llm_text(system: str, prompt: str) -> str:
    response = llm.invoke([
        SystemMessage(content=system),
        HumanMessage(content=prompt),
    ])
    return response.content


def _safe_json(text: str) -> dict:
    try:
        start = text.index("{")
        end   = text.rindex("}") + 1
        return json.loads(text[start:end])
    except (ValueError, json.JSONDecodeError):
        return {}


def supervisor_agent(state: TravelState) -> dict:
    query = state["user_query"]

    guardrail_raw = _llm_text(
        "You are an input validation guardrail. Return strict JSON only.",
        f"""Is this a valid travel planning request? Return only this JSON:
{{"allowed": true, "reason": ""}}

Request: {query}""",
    )

    guardrail = _safe_json(guardrail_raw)
    if not guardrail.get("allowed", True):
        reason = guardrail.get("reason", "Request not accepted.")
        return {
            "selected_agents":      [],
            "trip_constraints":     {},
            "supervisor_reasoning": reason,
            "final_response":       reason,
            "messages":             [AIMessage(content=reason)],
            "llm_calls":            state.get("llm_calls", 0) + 1,
        }

    raw = _llm_text(
        "You route travel queries to specialist agents. Return strict JSON only.",
        f"""You manage a travel planning system called GoBeyond.

Pick which agents are needed for this request.

Agents available:
- flight_agent: flights, airports, airlines, airfare
- hotel_agent: hotels, accommodation, neighbourhoods  
- weather_agent: weather, climate, packing, forecast
- budget_agent: cost analysis, budget feasibility
- itinerary_agent: day-by-day travel plan (always include this)

Return only this JSON:
{{
  "selected_agents": ["flight_agent", "hotel_agent", "weather_agent", "budget_agent", "itinerary_agent"],
  "trip_constraints": {{
    "destination": "",
    "origin": "",
    "duration": "",
    "budget": "",
    "travel_style": "",
    "special_preferences": []
  }},
  "reasoning": ""
}}

Request: {query}""",
    )

    parsed = _safe_json(raw)
    if not parsed:
        parsed = {
            "selected_agents": ["flight_agent", "hotel_agent", "weather_agent", "budget_agent", "itinerary_agent"],
            "trip_constraints": {"destination": query, "origin": "", "duration": "", "budget": "", "travel_style": "", "special_preferences": []},
            "reasoning": "Running all agents.",
        }

    return {
        "selected_agents":      parsed["selected_agents"],
        "trip_constraints":     parsed["trip_constraints"],
        "supervisor_reasoning": parsed["reasoning"],
        "messages":             [AIMessage(content="Supervisor done.")],
        "llm_calls":            state.get("llm_calls", 0) + 1,
    }


def flight_agent(state: TravelState) -> dict:
    query       = state["user_query"]
    constraints = state.get("trip_constraints", {})
    destination = constraints.get("destination", query)

    try:
        airports = asyncio.run(list_airports(destination, limit=10))
        airlines = asyncio.run(list_airlines("", limit=10))
    except Exception:
        airports = airlines = "Unavailable"

    result = _llm_text(
        "You are a flight planning specialist.",
        f"""Give flight guidance for this trip.

Request: {query}
Constraints: {json.dumps(constraints, indent=2)}
Airports: {str(airports)[:3000]}
Airlines: {str(airlines)[:3000]}

Cover: departure/arrival airports, airlines, duration, fare estimate, booking tips.""",
    )

    return {
        "flight_results": result,
        "messages":        [AIMessage(content="Flight agent done.")],
        "llm_calls":       state.get("llm_calls", 0) + 1,
    }


def hotel_agent(state: TravelState) -> dict:
    query = f"Best hotels and areas to stay for: {state['user_query']}"
    try:
        result = asyncio.run(tavily_search(query))
    except Exception as exc:
        result = f"Hotel search unavailable: {exc}"
    return {
        "hotel_results": str(result),
        "messages":       [AIMessage(content="Hotel agent done.")],
    }


def weather_agent(state: TravelState) -> dict:
    city = state.get("trip_constraints", {}).get("destination", state["user_query"])
    try:
        weather_data  = asyncio.run(current_weather(city))
        forecast_data = asyncio.run(forecast(city))
        result = f"Current weather:\n{weather_data}\n\nForecast:\n{forecast_data}"
    except Exception as exc:
        result = f"Weather unavailable: {exc}"
    return {
        "weather_results": result,
        "messages":         [AIMessage(content="Weather agent done.")],
    }


def budget_agent(state: TravelState) -> dict:
    result = _llm_text(
        "You are a travel budget analyst.",
        f"""Analyse budget feasibility for this trip.

Request: {state['user_query']}
Constraints: {json.dumps(state.get('trip_constraints', {}), indent=2)}
Flights: {state.get('flight_results', 'N/A')}
Hotels: {state.get('hotel_results', 'N/A')}
Weather: {state.get('weather_results', 'N/A')}

Give: cost breakdown, risk areas, money-saving tips, feasibility verdict.""",
    )
    return {
        "budget_results": result,
        "messages":        [AIMessage(content="Budget agent done.")],
        "llm_calls":       state.get("llm_calls", 0) + 1,
    }


def itinerary_agent(state: TravelState) -> dict:
    result = _llm_text(
        "You are an expert travel itinerary planner.",
        f"""Build a day-by-day travel itinerary.

Request: {state['user_query']}
Constraints: {json.dumps(state.get('trip_constraints', {}), indent=2)}
Flights: {state.get('flight_results', 'N/A')}
Hotels: {state.get('hotel_results', 'N/A')}
Weather: {state.get('weather_results', 'N/A')}
Budget: {state.get('budget_results', 'N/A')}

Format each day with morning, afternoon, evening sections.""",
    )

    return {
        "itinerary":        result,
        "approval_request": f"Please review this plan and approve or give feedback.\n\n{result}",
        "messages":         [AIMessage(content="Draft itinerary ready.")],
        "llm_calls":        state.get("llm_calls", 0) + 1,
    }


def human_approval_agent(state: TravelState) -> dict:
    feedback = interrupt({
        "question":         "Do you approve this itinerary?",
        "draft_itinerary":  state.get("itinerary", ""),
        "approval_request": state.get("approval_request", ""),
        "expected_response": {"approved": True, "feedback": ""},
    })
    return {
        "approved":       feedback.get("approved", False),
        "human_feedback": feedback.get("feedback", ""),
        "messages":       [AIMessage(content="Human approval recorded.")],
    }


def final_response_agent(state: TravelState) -> dict:
    approved = state.get("approved", False)

    if approved:
        prompt = f"""The traveller approved this itinerary. Write the final polished travel plan.

Itinerary:
{state.get('itinerary', '')}

Budget notes:
{state.get('budget_results', '')}"""
    else:
        prompt = f"""The traveller wants revisions. Improve the plan based on their feedback.

Original request: {state['user_query']}
Draft: {state.get('itinerary', '')}
Feedback: {state.get('human_feedback', '')}
Budget notes: {state.get('budget_results', '')}"""

    result = _llm_text("You write final travel plans for GoBeyond.", prompt)

    return {
        "final_response": result,
        "messages":        [AIMessage(content=result)],
        "llm_calls":       state.get("llm_calls", 0) + 1,
    }