# Manipal Airlines

Manipal Airlines is a Django-based flight booking system with two LangGraph agents connected to the same SQLite-backed data model. The project combines a customer-facing booking assistant with an autonomous operations agent that keeps inventory, discounts, and scheduling updates current.

## Overview

The application includes:

- A searchable flight booking experience built in Django.
- A conversational booking agent that interprets natural-language requests.
- A management agent that handles automated operational workflows.
- APScheduler jobs for recurring tasks such as flight generation, discount assignment, and reporting.
- Shared discount logic so operational updates are immediately visible in the booking flow.

## Booking Agent

The booking workflow is implemented in `agents/booking_agent/agent.py` and uses a LangGraph pipeline:

1. Parse the user’s natural-language request.
2. Search matching flights.
3. Fetch active discounts for the customer.
4. Apply the best available discount to each flight option.
5. Rank flights and return a plain-English response.

Example:

```python
from agents.booking_agent import run_booking_agent

result = run_booking_agent(1, "I want a flight from Mumbai to Delhi next weekend")
print(result["response"])
```

### What it does

- Converts natural-language trip requests into structured search intents.
- Finds flights by source, destination, date range, passenger count, and cabin class.
- Reads the user’s active and unused discounts from the shared database layer.
- Applies the best discount before presenting travel options.
- Ranks flights and explains the most relevant choices to the user.

### AI and fallback behavior

The booking agent uses Gemini from Google AI Studio when `GOOGLE_API_KEY` is configured. If no key is present, it falls back to a deterministic local parser for common route and date patterns so offline development and tests still work.

## Automated Workflows

The management agent in `agents/management_agent/agent.py` supports three actions:

### `schedule`

Creates the next day’s sample routes and removes stale flights.

- Adds upcoming flights without duplicating existing flight numbers.
- Removes expired flights or deactivates flights that are no longer valid.
- Keeps the schedule fresh for the next operating window.

### `loyalty`

Reviews travel patterns and assigns loyalty-based discounts.

- Identifies frequent flyers and inactive users.
- Assigns one active loyalty or re-engagement discount per qualifying customer.
- Notifies users about the newly issued discount.

### `report`

Generates a compact operational summary.

- Counts flights added.
- Counts flights removed or deactivated.
- Summarizes discounts assigned during the run.

## Scheduler

The recurring automation lives in `agents/management_agent/scheduler.py`.

Scheduled jobs include:

- Daily flight refresh at the configured schedule time.
- Weekly loyalty review and discount assignment.
- Daily operations report generation.

Start the scheduler with:

```bash
python -m agents.management_agent.scheduler
```

This keeps the system operational without manual intervention, and the management agent updates the same database used by the booking experience.

## Setup

```bash
cd "Manipal Airlines"
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Optional Gemini configuration:

```bash
export GOOGLE_API_KEY="your-google-ai-studio-key"
export GEMINI_MODEL="gemini-2.0-flash"
```

Never commit API keys. If a key has ever been exposed, rotate it in Google AI Studio.

## Testing

```bash
python manage.py test
python manage.py check
```

## Project Structure

```text
Manipal Airlines/
├── agents/
│   ├── booking_agent/        # Natural-language flight search and pricing flow
│   └── management_agent/     # Operational scheduling, loyalty logic, and reporting
├── airline_project/          # Django settings and URL config
├── flights/                  # Booking models, views, templates, and migrations
├── shared/                   # Shared DB access and configuration helpers
├── static/                   # Front-end CSS and JavaScript
├── db.sqlite3                # Local SQLite database
├── manage.py                 # Django management entry point
├── requirements.txt          # Python dependencies
├── project_context.md        # Project reference context
├── capture.py                # Local capture utilities
├── generate_report.py        # Reporting helper
├── README.md                 # Project documentation
└── .venv                     # Local virtual environment
```

## Architecture Notes

- The shared `UserDiscount` model acts as the communication link between operations and customer booking logic.
- Management tasks write discount and flight data to the same persistent store that the booking agent reads.
- This makes the airline system operationally aware while still keeping the customer-facing interaction conversational and user-friendly.
