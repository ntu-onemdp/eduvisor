def response_handler(status_code, status_message, data=None):
    """Generates a standardised API response."""
    return {
        "code": status_code,
        "status": status_message,
        "data": data
    }