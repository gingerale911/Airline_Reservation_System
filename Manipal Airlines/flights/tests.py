from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

from django.contrib.auth.models import User
from django.test import TestCase

from agents.booking_agent.tools import apply_best_discount, parse_nlp_query, rank_flights
from agents.management_agent.tools import assign_discount


class AgentToolsTests(TestCase):
	def test_best_discount_uses_highest_active_discount(self):
		discounts = [SimpleNamespace(discount_pct=10), SimpleNamespace(discount_pct=15)]
		price, selected = apply_best_discount(Decimal('1000.00'), discounts)
		self.assertEqual(price, Decimal('850.00'))
		self.assertEqual(selected.discount_pct, 15)

	def test_parser_fallback_extracts_route_and_passengers(self):
		intent = parse_nlp_query('Fly from Mumbai to Delhi tomorrow for 2 passengers')
		self.assertEqual(intent['source'], 'mumbai')
		self.assertEqual(intent['destination'], 'delhi')
		self.assertEqual(intent['passengers'], 2)
		self.assertEqual(intent['date_from'], (date.today() + timedelta(days=1)).isoformat())

	def test_rank_flights_returns_explanation(self):
		flight = SimpleNamespace(
			flight_number='MA101', origin=SimpleNamespace(city='Mumbai'),
			destination=SimpleNamespace(city='Delhi'), departure_time=SimpleNamespace(hour=8),
		)
		ranked = rank_flights([{
			'flight': flight, 'price': Decimal('3200'),
			'duration_minutes': 130, 'stops_count': 0,
		}])
		self.assertEqual(ranked[0]['flight'].flight_number, 'MA101')
		self.assertIn('MA101', ranked[0]['explanation'])

	def test_discount_assignment_is_idempotent_for_active_discount(self):
		user = User.objects.create_user(username='flyer', password='password')
		expiry = date.today() + timedelta(days=30)
		first, created = assign_discount(user.id, 15, expiry, 'loyalty')
		second, created_again = assign_discount(user.id, 10, expiry, 're_engagement')
		self.assertTrue(created)
		self.assertFalse(created_again)
		self.assertEqual(first.pk, second.pk)
