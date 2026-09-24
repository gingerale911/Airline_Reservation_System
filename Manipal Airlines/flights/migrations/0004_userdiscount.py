from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flights', '0003_booking_selected_seats_alter_flight_airline'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDiscount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_pct', models.FloatField(help_text='Discount percentage (e.g. 15.0 for 15%)')),
                ('valid_until', models.DateField()),
                ('reason', models.CharField(choices=[('loyalty', 'Loyalty Reward'), ('re_engagement', 'Re-engagement Offer')], max_length=50)),
                ('is_used', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discounts', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]