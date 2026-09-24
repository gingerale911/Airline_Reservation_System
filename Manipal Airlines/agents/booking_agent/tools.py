"""Flight search and pricing helpers for the booking graph."""
import json
import re
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Q

from shared.config import GEMINI_MODEL, GOOGLE_API_KEY
from shared.db_interface import active_discounts, setup_django


def apply_best_discount(price, discounts):
    """Return the discounted Decimal price and the selected discount object."""
    discount = max(discounts, key=lambda item: item.discount_pct, default=None)
    if not discount:
        return Decimal(str(price)), None
    final_price = Decimal(str(price)) * (Decimal('1') - Decimal(str(discount.discount_pct)) / Decimal('100'))
    return final_price.quantize(Decimal('0.01')), discount


def parse_nlp_query(raw_text):
    if GOOGLE_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            response = genai.GenerativeModel(GEMINI_MODEL).generate_content(
                f"Extract travel intent from this query as JSON only. Keys: source, destination, "
                f"date_from, date_to, passengers, cabin_class. Query: {raw_text}"
            )
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except (ValueError, TypeError, json.JSONDecodeError):
            pass

    text = raw_text.lower()
    passengers_match = re.search(r'(\d+)\s*(?:passenger|people|travell?ers?)', text)
    cabin = 'business' if 'business' in text else 'economy'
    dates = re.findall(r'\d{4}-\d{2}-\d{2}', text)
    today = date.today()
    if 'tomorrow' in text:
        date_from = date_to = today + timedelta(days=1)
    elif 'next weekend' in text:
        days_until_saturday = (5 - today.weekday()) % 7 or 7
        date_from, date_to = today + timedelta(days=days_until_saturday), today + timedelta(days=days_until_saturday + 1)
    elif dates:
        date_from = date_to = date.fromisoformat(dates[0])
    else:
        date_from = date_to = None
    route = re.search(r'from\s+([a-z]{3,})\s+to\s+([a-z]{3,})', text)
    return {
        'source': route.group(1) if route else None,
        'destination': route.group(2) if route else None,
        'date_from': date_from.isoformat() if date_from else None,
        'date_to': date_to.isoformat() if date_to else None,
        'passengers': int(passengers_match.group(1)) if passengers_match else 1,
        'cabin_class': cabin,
    }


def search_flights(source, destination, date_from=None, date_to=None, passengers=1, cabin_class='economy'):
    setup_django()
    from flights.models import Airport, Flight
    airports = Airport.objects.filter(Q(code__iexact=source) | Q(city__iexact=source))
    destinations = Airport.objects.filter(Q(code__iexact=destination) | Q(city__iexact=destination))
    flights = Flight.objects.filter(origin__in=airports, destination__in=destinations, is_active=True)
    if date_from:
        flights = flights.filter(departure_time__date__gte=date_from)
    if date_to:
        flights = flights.filter(departure_time__date__lte=date_to)
    result = []
    for flight in flights.select_related('origin', 'destination'):
        available = flight.business_seats_available if cabin_class == 'business' else flight.economy_seats_available
        if available < passengers:
            continue
        price = flight.business_price if cabin_class == 'business' else flight.economy_price
        result.append({
            'flight': flight, 'price': price, 'original_price': price,
            'duration_minutes': max(0, int((flight.arrival_time - flight.departure_time).total_seconds() / 60)),
            'stops_count': len(json.loads(flight.stops or '[]')),
        })
    return result


def rank_flights(flights_with_prices):
    if not flights_with_prices:
        return []
    max_price = max(float(item['price']) for item in flights_with_prices) or 1
    max_duration = max(item['duration_minutes'] for item in flights_with_prices) or 1
    ranked = []
    for item in flights_with_prices:
        flight = item['flight']
        price_score = 1 - float(item['price']) / max_price
        duration_score = 1 - item['duration_minutes'] / max_duration
        time_score = 1 - abs(flight.departure_time.hour - 8) / 16
        stops_score = 1 if item['stops_count'] == 0 else 0.5 / item['stops_count']
        item['score'] = round(price_score * .4 + duration_score * .3 + time_score * .2 + stops_score * .1, 4)
        item['explanation'] = f"{flight.flight_number}: {flight.origin.city} to {flight.destination.city}, {item['price']:.2f}"
        ranked.append(item)
    return sorted(ranked, key=lambda item: item['score'], reverse=True)