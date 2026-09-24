# Manipal Airlines

Manipal Airlines is a Django reservation system with two independent LangGraph agents. Both agents use the same SQLite-backed Django models, so operational decisions made by the Management Agent are immediately visible to the conversational Booking Agent.

## What The Agents Do

### Management Agent

The management graph accepts `schedule`, `loyalty`, or `report`:

- `schedule` creates the next day's sample routes without duplicating flight numbers, then removes expired flights or deactivates flights with bookings.
- `loyalty` finds frequent and inactive flyers, assigns one active loyalty or re-engagement discount per user, and logs a notification stub.
- `report` returns a compact operational summary.

Run it directly from the project directory:

```bash
python manage.py shell -c "from agents.management_agent import run_management_agent; print(run_management_agent('report'))"
```

### Booking Agent

`run_booking_agent(user_id, query)` parses a natural-language request, searches available flights, applies the user's best active discount, ranks the results, and returns a plain-English response.

```python
from agents.booking_agent import run_booking_agent

result = run_booking_agent(1, "I want to fly from Mumbai to Delhi next weekend")
print(result["response"])
```

The parser uses Google AI Studio Gemini when `GOOGLE_API_KEY` is configured. Without a key, a deterministic local parser handles common routes and dates, which keeps tests and development offline.

## Scheduling

APScheduler is configured in `agents/management_agent/scheduler.py`:

- Daily at midnight: add tomorrow's flights and clean expired inventory.
- Monday at 02:00: analyze flyers and assign discounts.
- Daily at 06:00: generate a report.

Start the blocking scheduler with:

```bash
python -m agents.management_agent.scheduler
```

For production, run this process under a supervisor and ensure only one scheduler instance owns these jobs.

## Setup

```bash
cd "Manipal Airlines"
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Optional Gemini configuration:

```bash
export GOOGLE_API_KEY="your-google-ai-studio-key"
export GEMINI_MODEL="gemini-2.0-flash"
```

Never commit the key. If a key has been exposed in chat, shell history, or a repository, revoke it in Google AI Studio and create a replacement.

## Test

```bash
python manage.py test
python manage.py check
```

## Structure

```text
Manipal Airlines/
├── agents/
│   ├── booking_agent/       # Conversational search graph and pricing tools
│   └── management_agent/    # Inventory, loyalty, reporting, and scheduler
├── flights/                 # Django models, views, templates, and migrations
├── shared/                  # Django bootstrap and agent configuration
├── airline_project/         # Django settings and URL configuration
└── manage.py
```

The shared `UserDiscount` model is the communication contract: the Management Agent writes discounts, and the Booking Agent reads active, unused discounts during search.
