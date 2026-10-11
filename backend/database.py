"""
HiddenGem – Neo4j Database Connection
--------------------------------------
This module handles:
  1. Reading credentials from environment variables (.env file)
  2. Creating a Neo4j driver instance
  3. Verifying the connection with a lightweight query
  4. Closing the driver safely when the app shuts down

NOTE: Never hard-code credentials. Always use environment variables.
"""

import os
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from dotenv import load_dotenv

# Load variables from .env file (only used during local development)
load_dotenv()

# ── Read credentials from environment ───────────────────────────────────────
NEO4J_URI      = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")


def get_driver():
    """
    Create and return a Neo4j driver instance.

    The driver is a connection pool — it is cheap to keep open
    and expensive to create repeatedly, so we create it once
    at startup (see lifespan in main.py).
    """
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
    )
    return driver


def verify_connection(driver) -> dict:
    """
    Run a minimal Cypher query to confirm Neo4j is reachable.

    Returns a dict with:
      - connected (bool)
      - message   (str)
    """
    try:
        # driver.verify_connectivity() checks the bolt connection
        driver.verify_connectivity()

        # Run a simple query to confirm auth + query pipeline works
        with driver.session() as session:
            result = session.run("RETURN 1 AS ping")
            result.single()  # consume the result

        return {"connected": True, "message": "Neo4j is reachable"}

    except AuthError:
        return {
            "connected": False,
            "message": "Authentication failed – check NEO4J_USERNAME and NEO4J_PASSWORD",
        }
    except ServiceUnavailable:
        return {
            "connected": False,
            "message": "Neo4j is not reachable – check NEO4J_URI and that the database is running",
        }
    except Exception as exc:
        return {"connected": False, "message": f"Unexpected error: {str(exc)}"}


def close_driver(driver) -> None:
    """
    Cleanly close the Neo4j driver and release all connections.
    Call this when the application shuts down.
    """
    if driver is not None:
        driver.close()
