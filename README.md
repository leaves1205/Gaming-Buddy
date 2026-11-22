# Gaming-buddy

## Local setup

1. Create a local MySQL database and import `fast.sql` into it. Use a fresh database because this script recreates the application tables.
2. Set a password of your choice for the seeded admin account (`user_id = 1`, username `admin`) using your local database client. The import assigns random passwords to all seed accounts. The current backend expects the value in the `user.password` column as plain text, so use a dedicated local database and a password you do not reuse elsewhere.
3. Copy `fastapi/.env.example` to `fastapi/.env`. Fill in your local database settings and generate a unique JWT signing secret, for example with `python -c "import secrets; print(secrets.token_hex(32))"`. Keep these values in your local environment file.
4. In `fastapi/`, install the dependencies with `python -m pip install -r requirements.txt`, then run `python main.py`.
5. In a separate terminal, run `npm install` and `npm run dev` from `vue/`.
