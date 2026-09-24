"""Database operations used by the management graph."""
import json
from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Max
from django.utils import timezone

from shared.db_interface import setup_django


def add_daily_flights(target_date=None):
    setup_django()
    from flights.models import Airport, Flight
    target_date = target_date or (timezone.localdate() + timedelta(days=1))
    airports = list(Airport.objects.order_by('id')[:20])
    created = []
    for index, (origin, destination) in enumerate(zip(airports[::2], airports[1::2]), 1):
        number = f'MA{target_date.strftime("%m%d")}{index:02d}'
        if Flight.objects.filter(flight_number=number, departure_time__date=target_date).exists():
            continue
        departure = timezone.make_aware(timezone.datetime.combine(target_date, timezone.datetime.min.time()))
        departure += timedelta(hours=6 + index * 2)
        flight = Flight.objects.create(
            flight_number=number, origin=origin, destination=destination,
            departure_time=departure, arrival_time=departure + timedelta(hours=2, minutes=15),
            economy_price=Decimal('4500.00'), business_price=Decimal('10500.00'),
        )
        created.append(flight.flight_number)
    return created


def remove_expired_flights(buffer_hours=2):
    setup_django()
    from flights.models import Flight
    cutoff = timezone.now() - timedelta(hours=buffer_hours)
    expired = Flight.objects.filter(departure_time__lt=cutoff, is_active=True)
    removed, deactivated = [], []
    for flight in expired:
        if flight.bookings.filter(status='confirmed').exists():
            flight.is_active = False
            flight.save(update_fields=['is_active'])
            deactivated.append(flight.flight_number)
        else:
            removed.append(flight.flight_number)
            flight.delete()
    return {'removed': removed, 'deactivated': deactivated}


def frequent_flyers(limit=10, least=False):
    setup_django()
    from django.contrib.auth.models import User
    query = User.objects.filter(bookings__status='confirmed').annotate(
        completed_flights=Count('bookings', distinct=True),
        last_booking=Max('bookings__booking_date'),
    )
    ordering = ['completed_flights', 'last_booking'] if least else ['-completed_flights', '-last_booking']
    return list(query.order_by(*ordering)[:limit])


def assign_discount(user_id, discount_pct, valid_until, reason):
    setup_django()
    from flights.models import UserDiscount
    existing = UserDiscount.objects.filter(
        user_id=user_id, is_used=False, valid_until__gte=timezone.localdate(),
    ).first()
    if existing:
        return existing, False
    discount = UserDiscount.objects.create(
        user_id=user_id, discount_pct=discount_pct, valid_until=valid_until, reason=reason,
    )
    return discount, True


def notify_user(user_id, message):
    print(f'[management-agent] user={user_id}: {message}')
    return message