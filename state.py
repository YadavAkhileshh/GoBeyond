import operator
from typing import Annotated, Any
from langchain_core.messages import AnyMessage, HumanMessage


class TravelState(dict):
    messages:             Annotated[list[AnyMessage], operator.add]
    user_id:              str
    user_query:           str
    selected_agents:      list[str]
    trip_constraints:     dict[str, Any]
    supervisor_reasoning: str
    flight_results:       str
    hotel_results:        str
    weather_results:      str
    budget_results:       str
    itinerary:            str
    approval_request:     str
    human_feedback:       str
    approved:             bool
    final_response:       str
    llm_calls:            int


def default_state(user_query: str, user_id: str = "guest") -> dict:
    return {
        "messages":             [HumanMessage(content=user_query)],
        "user_id":              user_id,
        "user_query":           user_query,
        "selected_agents":      [],
        "trip_constraints":     {},
        "supervisor_reasoning": "",
        "flight_results":       "",
        "hotel_results":        "",
        "weather_results":      "",
        "budget_results":       "",
        "itinerary":            "",
        "approval_request":     "",
        "human_feedback":       "",
        "approved":             False,
        "final_response":       "",
        "llm_calls":            0,
    }
