from .tools import apply_best_discount, parse_nlp_query, rank_flights, search_flights
from shared.db_interface import active_discounts


def parse_intent_node(state):
    return {'parsed_intent': parse_nlp_query(state['raw_query'])}


def fetch_flights_node(state):
    intent = state['parsed_intent']
    return {'available_flights': search_flights(
        intent.get('source'), intent.get('destination'), intent.get('date_from'), intent.get('date_to'),
        intent.get('passengers', 1), intent.get('cabin_class', 'economy'),
    )}


def fetch_user_discounts_node(state):
    return {'user_discounts': active_discounts(state['user_id'])}


def apply_discounts_node(state):
    discounted = []
    for item in state.get('available_flights', []):
        final_price, discount = apply_best_discount(item['price'], state.get('user_discounts', []))
        item = {**item, 'price': final_price, 'discount_used': discount.discount_pct if discount else 0}
        discounted.append(item)
    return {'available_flights': discounted}


def rank_and_explain_node(state):
    ranked = rank_flights(state.get('available_flights', []))[:5]
    return {'ranked_results': ranked, 'response': '\n'.join(item['explanation'] for item in ranked) or 'No flights matched your request.'}