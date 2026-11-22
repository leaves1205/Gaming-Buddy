"""
Application entry point

Run from this directory to avoid a name conflict between the fastapi folder and the installed package.
    cd fastapi
    python main.py                                     # Port 8080 with auto-reload and colored logs
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload  # Equivalent command. Add --use-colors for color.
"""
import os  # Standard-library process and file operations
import signal  # Standard-library termination signals
from contextlib import asynccontextmanager  # Standard-library async context manager for lifespan
from multiprocessing import parent_process  # Standard-library check for a reload child process

# FastAPI application, requests, exceptions, middleware, responses and static mounts
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text  # SQLAlchemy raw SQL text

from core.config import settings  # Application settings
from core.database import engine  # Application database engine
from core.exceptions import ApiError, AuthError  # Application exceptions
from routers import ALL_ROUTERS  # Combined routers from all modules

os.system("")  # Enable ANSI colors in older Windows consoles. This is harmless in PyCharm and newer terminals.

HOST = "0.0.0.0"  # Listen on 0.0.0.0 to allow LAN access
PORT = 8080       # Keep the port in sync with the frontend Vite proxy

# ANSI codes for colored terminal logs
_GREEN = "\033[92m"  # Success (green)
_RED = "\033[91m"    # Failure (red)
_CYAN = "\033[96m"   # Highlight (cyan)
_GRAY = "\033[90m"   # Secondary text (gray)
_RESET = "\033[0m"   # Reset the color


# ==================== Startup checks =====================

def check_database() -> None:
    """Check the database connection at startup. Log a failure and abort startup."""
    target = f"mysql://{settings.db_host}:{settings.db_port}/{settings.db_name}"  # Connection target (host:port/database)
    print(f"Checking database connection: {target} ...")  # Progress message
    try:
        with engine.connect() as conn:  # Get a pooled connection and release it automatically
            version = conn.execute(text("SELECT VERSION()")).scalar()  # Read the MySQL version
        print(f"{_GREEN}[OK]{_RESET} Database connection established (MySQL {version})")  # Success message in green
    except Exception as e:
        print(f"{_RED}[FAIL]{_RESET} Database connection failed. Check the database configuration in fastapi/.env.")  # Failure message in red
        print(f"       Reason: {e}")  # Exception details
        # With --reload, stop the parent reloader before exiting the worker so it releases the terminal and port.
        if parent_process() is not None:  # A parent process indicates this is the reload worker
            try:
                os.kill(os.getppid(), signal.SIGTERM)  # Send SIGTERM to the parent reloader
            except OSError:
                pass  # Ignore the error if the parent process has already exited
        os._exit(1)  # Exit immediately, bypassing cleanup hooks such as atexit


@asynccontextmanager
async def lifespan(_: FastAPI):  # The app instance argument is unused
    # At startup, check the database and print a success message
    check_database()  # Abort startup if the database check fails
    print(f"{_GRAY}{'=' * 46}{_RESET}")  # Gray divider
    print(f"{_GREEN}Backend started successfully{_RESET}")  # Green heading
    print(f"Server URL: {_CYAN}http://localhost:{PORT}{_RESET}")  # Cyan URL with the port from PORT
    print(f"{_GRAY}{'=' * 46}{_RESET}")
    yield  # Startup runs before yield and shutdown runs after it
    # Release the database connection pool on shutdown
    engine.dispose()  # Close all pooled connections


app = FastAPI(  # DOCS_ENABLED in .env controls the documentation endpoints. Disable them in production if needed.
    title="fast", lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,  # Swagger documentation
    redoc_url="/redoc" if settings.docs_enabled else None,  # ReDoc documentation
    openapi_url="/openapi.json" if settings.docs_enabled else None,  # OpenAPI schema
)

# Allow cross-origin requests from any origin
app.add_middleware(  # Register the CORS middleware
    CORSMiddleware,
    allow_origin_regex=".*",  # Allow any origin
    allow_credentials=True,  # Allow cookies and other credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all request headers
    max_age=1800,  # Cache preflight results for 30 minutes
)


# ==================== Exception handling ====================

@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError):
    """Authentication failure returns HTTP 401 with {code:401, msg}"""
    return JSONResponse(status_code=401, content={"code": 401, "msg": exc.msg})  # The frontend uses this response to prompt users to sign in again


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    """Application errors return HTTP 500 with {code:500, msg}"""
    return JSONResponse(status_code=500, content={"code": 500, "msg": exc.msg})


# Map validation error types to English messages. Omit input values to protect sensitive data.
_VALIDATION_MESSAGES = {
    "missing": "is required",  # Required parameter is missing
    "int_parsing": "must be an integer",  # Integer parsing failed
    "integer_type": "must be an integer",  # Wrong type
    "string_type": "must be a string",  # Wrong type
    "bool_parsing": "must be a boolean",  # Boolean parsing failed
    "greater_than_equal": "is too small",  # Below the minimum, such as pageNum < 1
    "greater_than": "is too small",  # At or below the exclusive lower bound
    "less_than_equal": "is too large",  # Above the maximum, such as pageSize > 500
    "less_than": "is too large",  # At or above the exclusive upper bound
    "string_pattern_mismatch": "has an invalid format",  # Regex mismatch
    "string_too_short": "is too short",  # Below the minimum length, such as a password shorter than six characters
    "string_too_long": "is too long",  # Above the maximum length defined by the corresponding database column
    "json_invalid": "has an invalid format",  # JSON parsing failed
    "datetime_parsing": "must be a date and time",  # Datetime parsing failed
}


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Report the field and English message for the first request validation error"""
    msg = "Invalid request parameters"  # Fallback message when error details are unavailable
    if exc.errors():  # Use the detailed message when errors are available
        first = exc.errors()[0]  # Report just the first field error
        field = str(first.get("loc", ("?",))[-1])  # The final loc element is the field name, such as pageSize in ("query","pageSize")
        validation_message = _VALIDATION_MESSAGES.get(first.get("type", ""), "has an invalid format")  # Translate known error types and use a generic message for the rest
        msg = f"Invalid parameter: {field} {validation_message}"  # For example, "Invalid parameter: pageSize must be an integer"
    return JSONResponse(status_code=500, content={"code": 500, "msg": msg})


@app.exception_handler(Exception)
async def fallback_error_handler(request: Request, exc: Exception):
    """Fallback for unhandled exceptions (HTTP 500)"""
    return JSONResponse(status_code=500, content={"code": 500, "msg": str(exc) or "Operation failed"})  # Handle any otherwise unhandled exception


# ==================== Static files at /profile/** from {profile}/ ====================

_profile_dir = os.path.abspath(settings.profile)  # Absolute path to the uploads root
os.makedirs(os.path.join(_profile_dir, "avatar"), exist_ok=True)  # Ensure the avatar directory exists
os.makedirs(os.path.join(_profile_dir, "upload"), exist_ok=True)  # Ensure the upload directory exists
app.mount("/profile", StaticFiles(directory=_profile_dir), name="profile")  # Serve the local directory publicly at /profile/**


# ==================== Route registration ====================

# Register the routers listed in routers/__init__.py under ALL_ROUTERS. Add new routers there.
for _router in ALL_ROUTERS:
    app.include_router(_router)  # Register each module's router


# ==================== Startup when run directly ====================
# Equivalent to uvicorn main:app --host 0.0.0.0 --port 8080 --reload
# Reload requires the import string "main:app".

if __name__ == "__main__":  # Start only when this file is run directly
    import copy  # Standard-library deep copy for the logging template
    import uvicorn  # Import locally when running the file
    from uvicorn.config import LOGGING_CONFIG  # Default uvicorn logging dictionary

    log_config = copy.deepcopy(LOGGING_CONFIG)  # Copy the default configuration before editing it
    for handler in log_config["handlers"].values():  # Adjust the output stream for each handler
        if "stream" in handler:  # Change only the default and access stream handlers
            handler["stream"] = "ext://sys.stdout"  # Use stdout because PyCharm can render ANSI colors there without coloring the entire stderr line red

    uvicorn.run("main:app", host=HOST, port=PORT, reload=True, use_colors=True, log_config=log_config)  # Force ANSI colors because auto-detection can disable them in pipes or PyCharm
