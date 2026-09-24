from datetime import timedelta
from typing import Any

from django.utils import timezone

from . import tools


def router_node(state):
    return state


def add_flights_node(state):
    return {'flights_added': tools.add_daily_flights()}


def remove_old_flights_node(state):
    result = tools.remove_expired_flights()
    return {'flights_removed': result['removed'] + result['deactivated']}


def analyze_flyers_node(state):
    users = tools.frequent_flyers(10)
    least = tools.frequent_flyers(10, least=True)
    return {'top_flyers': [user.id for user in users], 'least_flyers': [user.id for user in least]}


def assign_discounts_node(state):
    actions = []
    expiry = timezone.localdate() + timedelta(days=30)
    for user_id in state.get('top_flyers', []):
        discount, created = tools.assign_discount(user_id, 15, expiry, 'loyalty')
        if created:
            actions.append({'user_id': user_id, 'discount_pct': discount.discount_pct, 'reason': 'loyalty'})
    for user_id in state.get('least_flyers', []):
        discount, created = tools.assign_discount(user_id, 10, expiry, 're_engagement')
        if created:
            actions.append({'user_id': user_id, 'discount_pct': discount.discount_pct, 'reason': 're_engagement'})
    return {'discount_actions': actions}


def notify_node(state):
    for action in state.get('discount_actions', []):
        tools.notify_user(action['user_id'], f"Your {action['discount_pct']}% {action['reason']} discount is ready.")
    return {}


def generate_report_node(state):
    return {'report': (
        f"Added {len(state.get('flights_added', []))} flights; "
        f"removed or deactivated {len(state.get('flights_removed', []))} flights; "
        f"assigned {len(state.get('discount_actions', []))} discounts."
    )}