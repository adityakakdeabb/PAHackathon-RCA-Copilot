def format_response(response):
    """Formats the response string for display."""
    return response.strip()

def validate_query(query):
    """Validates the user query to ensure it is not empty."""
    return bool(query and query.strip())

def process_query(query):
    """Processes the user query and prepares it for further handling."""
    # Placeholder for any processing logic
    return query.lower()