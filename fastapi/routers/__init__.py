"""
Central route registration

Create new feature modules such as student under routers/.
Import the module and add its router to ALL_ROUTERS below.
"""
from routers import auth, file, index, menu, profile, role, user  # Application routes by module

# Module routers in registration order. Append new modules here.
ALL_ROUTERS = [
    index.router,  # Home (public)
    auth.router,  # Sign-in, registration and sign-out
    user.router,  # User Management
    profile.router,  # Profile
    role.router,  # Role Management
    menu.router,  # Menu Management
    file.router,  # File upload
]
