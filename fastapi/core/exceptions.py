"""
Custom exceptions

- AuthError handles missing, expired or invalid credentials and returns HTTP 401 with {code:401, msg}
- ApiError handles application errors and returns HTTP 500 with {code:500, msg}
- Other application failures return HTTP 200 with code 500. See core/response.py.
"""


class AuthError(Exception):
    """Authentication failed because the token is missing, expired, invalid or revoked"""

    def __init__(self, msg: str = "Your session has expired. Please sign in again."):  # Default message
        self.msg = msg  # Store the message for the global exception handler
        super().__init__(msg)  # Also pass the message to the Exception base class


class ApiError(Exception):
    """Application error"""

    def __init__(self, msg: str):  # An error message is required
        self.msg = msg  # Store the message for the global exception handler
        super().__init__(msg)  # Also pass the message to the Exception base class
