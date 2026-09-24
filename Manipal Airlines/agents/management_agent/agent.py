from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from .nodes import (add_flights_node, analyze_flyers_node, assign_discounts_node,
                    generate_report_node, notify_node, remove_old_flights_node)


class ManagementState(TypedDict, total=False):
    action: str
    flights_added: list[str]
    flights_removed: list[str]
    discount_actions: list[dict]
    report: str
    top_flyers: list[int]
    least_flyers: list[int]


def route(state):
    return state.get('action', 'schedule')


graph = StateGraph(ManagementState)
graph.add_node('add_flights', add_flights_node)
graph.add_node('remove_old_flights', remove_old_flights_node)
graph.add_node('analyze_flyers', analyze_flyers_node)
graph.add_node('assign_discounts', assign_discounts_node)
graph.add_node('notify', notify_node)
graph.add_node('generate_report', generate_report_node)
graph.add_conditional_edges(START, route, {
    'schedule': 'add_flights', 'loyalty': 'analyze_flyers', 'report': 'generate_report',
})
graph.add_edge('add_flights', 'remove_old_flights')
graph.add_edge('remove_old_flights', END)
graph.add_edge('analyze_flyers', 'assign_discounts')
graph.add_edge('assign_discounts', 'notify')
graph.add_edge('notify', END)
graph.add_edge('generate_report', END)
management_graph = graph.compile()


def run_management_agent(action='schedule'):
    return management_graph.invoke({'action': action})