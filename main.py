import os
import asyncio
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import DocumentNotFoundException

# Load environment variables from .env file
load_dotenv()


USER_ID = "Chris"


# --- Couchbase Memory Class ---
class CouchbaseMemory:
    def __init__(
        self,
        conn_str,
        username,
        password,
        bucket_name,
        scope_name="travel",
        collection_name="memory",
    ):
        auth = PasswordAuthenticator(username, password)
        options = ClusterOptions(auth)
        options.apply_profile("wan_development")  # Required for Capella cloud access
        self.cluster = Cluster(conn_str, options)
        self.bucket = self.cluster.bucket(bucket_name)
        self.scope = self.bucket.scope(scope_name)
        self.collection = self.scope.collection(collection_name)
        # print("[Memory System] Connected to Couchbase Capella")

    def _doc_id(self, user_id: str):
        return f"user::{user_id}"

    def add(self, user_id: str, category: str, data: str):
        doc_id = self._doc_id(user_id)
        try:
            doc = self.collection.get(doc_id).content_as[dict]
        except DocumentNotFoundException:
            doc = {}

        doc.setdefault(category, [])
        if data not in doc[category]:
            doc[category].append(data)
            self.collection.upsert(doc_id, doc)
            # print(
            #     f"[Memory System] Saved data for user '{user_id}' in category '{category}': '{data}'"
            # )
        return True

    def search_by_category(self, user_id: str, category: str) -> list:
        doc_id = self._doc_id(user_id)
        try:
            doc = self.collection.get(doc_id).content_as[dict]
            results = doc.get(category, [])
        except DocumentNotFoundException:
            results = []
        # print(
        #     f"[Memory System] Retrieved {len(results)} items from category '{category}' for user '{user_id}'."
        # )
        return results


# --- Replace with your Capella credentials ---
COUCHBASE_CONN_STR = os.getenv("COUCHBASE_CONN_STR")
COUCHBASE_USERNAME = os.getenv("COUCHBASE_USERNAME")
COUCHBASE_PASSWORD = os.getenv("COUCHBASE_PASSWORD")
COUCHBASE_BUCKET = os.getenv("COUCHBASE_BUCKET")

persistent_data = CouchbaseMemory(
    conn_str=COUCHBASE_CONN_STR,
    username=COUCHBASE_USERNAME,
    password=COUCHBASE_PASSWORD,
    bucket_name=COUCHBASE_BUCKET,
    scope_name="_default",  # match your setup
    collection_name="_default",  # match your setup
)


def save_user_preference(category: str, preference: str) -> dict:
    user_id = getattr(save_user_preference, "user_id", USER_ID)
    persistent_data.add(user_id=user_id, category=category, data=preference)
    return {
        "status": "success",
        "message": f"Preference saved in category '{category}'.",
    }


def retrieve_user_preferences(category: str) -> dict:
    user_id = getattr(retrieve_user_preferences, "user_id", USER_ID)
    results = persistent_data.search_by_category(user_id=user_id, category=category)
    return {"status": "success", "preferences": results, "count": len(results)}


def find_flights(destination: str, departure_date: str) -> dict:
    user_id = getattr(save_user_preference, "user_id", USER_ID)
    travel_prefs = persistent_data.search_by_category(user_id, "travel_preferences")

    airline_pref = None
    seat_pref = None

    for pref in travel_prefs:
        if (
            "window" in pref.lower()
            or "aisle" in pref.lower()
            or "middle" in pref.lower()
        ):
            seat_pref = pref
        elif (
            "air" in pref.lower()
            or "jet" in pref.lower()
            or "airlines" in pref.lower()
            or len(pref.split()) >= 1
        ):
            airline_pref = pref

    if not airline_pref:
        return {
            "status": "error",
            "message": "No airline preference found. Please add a preferred airline first.",
        }

    flight = {
        "airline": airline_pref,
        "flight_number": f"{airline_pref[:2].upper()}{random.randint(100, 999)}",
        "departure_time": (
            datetime.now() + timedelta(hours=random.randint(2, 5))
        ).strftime("%H:%M"),
        "arrival_time": (
            datetime.now() + timedelta(hours=random.randint(10, 14))
        ).strftime("%H:%M"),
        "price": f"{random.randint(800, 1800)} EUR",
        "notes": (
            f"Seat preference '{seat_pref}' is available."
            if seat_pref
            else "Standard seat options available."
        ),
    }

    # print(
    #     f"INFO: Generated 1 flight to {destination} on {departure_date} for preferred airline: {airline_pref}"
    # )

    return {"status": "success", "flights": [flight]}


wellness_agent = Agent(
    name="wellness_assistant",
    model="gemini-2.5-flash",
    description="A smart and supportive wellness assistant that helps users log, track, and optimize their health and recovery.",
    instruction="""
You are a supportive and intelligent Wellness Assistant. You help users manage their wellbeing through daily logging, tracking, and recommendations.

Your capabilities:
- Users may log their sleep, calories, workouts, weightlifting, injuries, diet, medical updates, mood, or recovery needs.
- Always use `save_user_preference` to store the user's log entries, using the appropriate category (e.g., 'sleep', 'workout', 'injury').
- Use `retrieve_user_preferences` to reference past entries when helping the user reflect or make decisions.
- Offer helpful feedback and guidance when appropriate (e.g., reminding them to rest if injured, praising consistent sleep, suggesting healthy habits).
- If no relevant logs exist yet, kindly prompt the user to start tracking those categories.

Respond conversationally and empathetically — your goal is to make daily wellbeing easier to manage and reflect on.
""",
    tools=[save_user_preference, retrieve_user_preferences],
)


session_service = InMemorySessionService()
APP_NAME = "travel_assistant_app"
SESSION_ID = "session_001"

runner = Runner(
    agent=wellness_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def call_agent_async(query: str, user_id: str, session_id: str):
    # print(f"\n>>> User ({user_id}): {query}")
    content = types.Content(role="user", parts=[types.Part(text=query)])
    setattr(save_user_preference, "user_id", user_id)
    setattr(retrieve_user_preferences, "user_id", user_id)

    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text
            # print(f"<<< Assistant: {final_response}")
            return final_response

    return "No response received."


async def interactive_chat():
    # print("--- Starting Interactive Travel Assistant ---")
    # print("Type 'quit' to end the session.")
    while True:
        user_query = input("\n> ")
        if user_query.lower() in ["quit", "exit"]:
            # print("Ending session. Goodbye!")
            break
        await call_agent_async(query=user_query, user_id=USER_ID, session_id=SESSION_ID)


async def create_session():
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )


if __name__ == "__main__":
    if (
        not os.getenv("GOOGLE_API_KEY")
        or os.getenv("GOOGLE_API_KEY") == "YOUR_GOOGLE_API_KEY_HERE"
    ):
        print(
            "ERROR: Please set your GOOGLE_API_KEY environment variable to run this script."
        )
    else:
        asyncio.run(create_session())
        asyncio.run(interactive_chat())
