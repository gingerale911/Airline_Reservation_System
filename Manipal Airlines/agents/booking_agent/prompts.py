INTENT_PROMPT = """Extract travel intent from the user query as JSON only.
Keys: source, destination, date_from, date_to, passengers, cabin_class.
Use ISO dates when a date is present; use null when unknown. Query: {query}"""