from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .nodes import (apply_discounts_node, fetch_flights_node,
                    fetch_user_discounts_node, parse_intent_node,
                    rank_and_explain_node)


class BookingState(TypedDict, total=False):
    user_id: int
    raw_query: str
    parsed_intent: dict
    available_flights: list[dict]
    user_discounts: list
    ranked_results: list[dict]
    response: str


graph = StateGraph(BookingState)
for name, node in (
    ('parse_intent', parse_intent_node), ('fetch_flights', fetch_flights_node),
    ('fetch_user_discounts', fetch_user_discounts_node), ('apply_discounts', apply_discounts_node),
    ('rank_and_explain', rank_and_explain_node),
):
    graph.add_node(name, node)
graph.add_edge(START, 'parse_intent')
graph.add_edge('parse_intent', 'fetch_flights')
graph.add_edge('fetch_flights', 'fetch_user_discounts')
graph.add_edge('fetch_user_discounts', 'apply_discounts')
graph.add_edge('apply_discounts', 'rank_and_explain')
graph.add_edge('rank_and_explain', END)
booking_graph = graph.compile()


def run_booking_agent(user_id, query):
    return booking_graph.invoke({'user_id': user_id, 'raw_query': query})