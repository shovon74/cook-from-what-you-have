import os
import psycopg

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://chef_user:chef_password@localhost:5432/personal_chef_db"
)

def get_connection():
    """Returns an active connection to PostgreSQL."""
    return psycopg.connect(DATABASE_URL)

def init_db():
    """Initializes tables: users and recipes with foreign keys."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # 2. Recipes table (linked to users via foreign key)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS recipes (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    thread_id TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()

def get_or_create_user(name: str, email: str) -> int:
    """Finds an existing user by email, or creates a new one. Returns user_id."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Check if user already exists
            cur.execute("SELECT id FROM users WHERE email = %s;", (email,))
            row = cur.fetchone()
            if row:
                return row[0]

            # If new user, insert and return new id
            cur.execute("""
                INSERT INTO users (name, email)
                VALUES (%s, %s)
                RETURNING id;
            """, (name, email))
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id

def save_recipe(user_id: int, thread_id: str, prompt: str, response: str):
    """Saves a recipe generated for a specific user and conversation thread."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO recipes (user_id, thread_id, prompt, response)
                VALUES (%s, %s, %s, %s);
            """, (user_id, thread_id, prompt, response))
        conn.commit()

def get_user_recipes(user_id: int):
    """Retrieves all past recipes and conversations for a specific user."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT prompt, response, created_at 
                FROM recipes 
                WHERE user_id = %s 
                ORDER BY created_at DESC;
            """, (user_id,))
            return cur.fetchall()
