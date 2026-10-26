"""Background AI Worker: Consumes cooking requests from Redis and saves to PostgreSQL."""

import json
import os
import time
import redis

import db
from agent import ask, build_agent

# Read connection string from environment (or default to localhost)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Name of the Redis Queue list
QUEUE_NAME = "cooking_tasks"


def start_worker():
    print(f"[*] Connecting to Redis at: {REDIS_URL}")
    r = redis.from_url(REDIS_URL)

    # Initialize the AI Agent once
    print("[*] Initializing AI Chef agent...")
    agent = build_agent()

    # Ensure PostgreSQL tables are ready
    db.init_db()

    print(f"[*] Worker started! Listening for jobs on queue: '{QUEUE_NAME}'...")

    while True:
        try:
            # BLPOP: Blocks and waits until a job arrives. Timeout of 2s prevents hanging forever.
            task_data = r.blpop(QUEUE_NAME, timeout=2)

            if task_data is None:
                # No job in queue, loop continues and checks again
                continue

            # task_data is a tuple: (b'cooking_tasks', b'{"job_id": "...", ...}')
            _, raw_payload = task_data
            job = json.loads(raw_payload.decode("utf-8"))

            job_id = job["job_id"]
            user_id = job["user_id"]
            thread_id = job["thread_id"]
            prompt = job["prompt"]

            print(f"\n[+] Received Job [{job_id}] for User #{user_id}: '{prompt}'")

            # 1. Update job status in Redis to "processing"
            r.set(f"job:{job_id}", json.dumps({"status": "processing"}), ex=3600)

            # 2. Run the AI Agent (Gemini + Tavily web search)
            reply = ask(agent, prompt, thread_id)

            # 3. Save finished recipe into PostgreSQL
            db.save_recipe(user_id, thread_id, prompt, reply)

            # 4. Mark job as "completed" in Redis so frontend knows it is ready
            r.set(
                f"job:{job_id}",
                json.dumps({"status": "completed", "response": reply}),
                ex=3600,  # Expire after 1 hour to save RAM
            )

            print(f"[✓] Job [{job_id}] completed and saved to PostgreSQL!")

        except KeyboardInterrupt:
            print("\n[*] Stopping worker gracefully...")
            break
        except Exception as e:
            print(f"[!] Error processing task: {e}")
            if "job_id" in locals():
                r.set(f"job:{job_id}", json.dumps({"status": "failed", "error": str(e)}), ex=3600)
            time.sleep(1)


if __name__ == "__main__":
    start_worker()
