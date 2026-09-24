"""Small ORM boundary shared by both autonomous agents."""
import os


def setup_django():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airline_project.settings')
    import django
    django.setup()


def active_discounts(user_id):
    setup_django()
    from django.utils import timezone
    from flights.models import UserDiscount
    return list(UserDiscount.objects.filter(
        user_id=user_id, is_used=False, valid_until__gte=timezone.localdate(),
    ))