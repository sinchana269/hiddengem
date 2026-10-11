"""
HiddenGem – FastAPI Backend Entry Point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import get_driver, verify_connection, close_driver
from schema import initialise_schema
import import_data

from nlp.query_parser import parse_query
from recommendation.recommender import recommend_destinations
from itinerary import build_itinerary


# ── Lifespan ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    app.state.neo4j_driver = get_driver()

    yield

    # SHUTDOWN
    close_driver(app.state.neo4j_driver)


# ── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="HiddenGem API",
    description="Intelligent Karnataka Tourism Discovery Platform",
    version="0.1.0",
    lifespan=lifespan,
)


# ── CORS ────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Models ──────────────────────────────────────────────────────────

class RecommendRequest(BaseModel):
    query: str


class ItineraryRequest(BaseModel):
    query: str


# ── Neo4j Data Retrieval ────────────────────────────────────────────────────

def get_destination_data(driver):
    """
    Fetch destination information from Neo4j.

    The query uses destination relationships by node label,
    so it does not depend on hardcoded relationship names.
    """

    query = """
    MATCH (d:Destination)

    OPTIONAL MATCH (d)-[]->(a:Attraction)
    WITH d, collect(DISTINCT a.name) AS attractions

    OPTIONAL MATCH (d)-[]->(act:Activity)
    WITH d, attractions, collect(DISTINCT act.name) AS activities

    OPTIONAL MATCH (d)-[]->(f:Food)
    WITH d, attractions, activities,
         collect(DISTINCT f.name) AS food

    RETURN
        d.name AS name,
        d.description AS description,
        d.category AS category,
        d.best_season AS best_season,
        d.latitude AS latitude,
        d.longitude AS longitude,
        d.image_url AS image_url,
        attractions,
        activities,
        food

    ORDER BY d.name
    """

    with driver.session() as session:
        result = session.run(query)

        return [
            record.data()
            for record in result
        ]


# ── Basic Routes ────────────────────────────────────────────────────────────

@app.get("/")
def read_root():
    return {
        "message": "Welcome to HiddenGem API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }


@app.get("/api/health")
def api_health_check():
    return {
        "status": "ok",
        "service": "HiddenGem API",
    }


# ── Neo4j Health ────────────────────────────────────────────────────────────

@app.get("/api/neo4j-health")
def neo4j_health_check():
    """
    Verify that the backend can reach Neo4j.
    """

    result = verify_connection(
        app.state.neo4j_driver
    )

    return result


# ── Schema ──────────────────────────────────────────────────────────────────

@app.post("/api/schema/init")
def init_schema():
    """
    Apply constraints and indexes to Neo4j.
    """

    result = initialise_schema(
        app.state.neo4j_driver
    )

    return result


# ── Import ──────────────────────────────────────────────────────────────────

@app.post("/api/import")
def import_destinations():
    """
    Import the 5 seed Karnataka destinations into Neo4j.
    """

    records = import_data.load_destinations()

    with app.state.neo4j_driver.session() as session:

        for record in records:
            import_data.import_destination(
                session,
                record,
            )

    return {
        "status": "import complete",
        "destinations_imported": len(records),
        "note": "Used MERGE – no duplicates created",
    }


# ── Recommendation API ──────────────────────────────────────────────────────

@app.post("/api/recommend")
def recommend(request: RecommendRequest):
    """
    Convert a natural-language tourism query into
    preferences, retrieve destinations from Neo4j,
    and calculate recommendations.
    """

    # 1. Validate query

    if not request.query or not request.query.strip():

        return {
            "status": "error",
            "message": "Please enter a tourism query.",
            "preferences": None,
            "recommendations": [],
        }

    # 2. NLP parsing

    preferences = parse_query(
        request.query
    )

    # 3. Retrieve destinations

    destinations = get_destination_data(
        app.state.neo4j_driver
    )

    # 4. Calculate recommendations

    recommendations = recommend_destinations(
        preferences,
        destinations,
    )

    # 5. Return result

    return {
        "status": "success",
        "preferences": preferences,
        "recommendations": recommendations,
        "total_results": len(
            recommendations
        ),
    }


# ── Destination API ─────────────────────────────────────────────────────────

@app.get("/api/destination/{destination_id}")
def get_destination(
    destination_id: str,
):
    """
    Return detailed information for one
    destination from Neo4j.
    """

    query = """
    MATCH (d:Destination)

    WHERE
        toLower(
            replace(d.name, ' ', '-')
        ) = toLower($destination_id)

        OR

        toLower(d.name)
        = toLower($destination_id)

    CALL {
        WITH d

        MATCH (d)-[:HAS_PLACE]->(a:Attraction)

        RETURN collect(
            DISTINCT a.name
        ) AS attractions
    }

    CALL {
        WITH d

        MATCH (d)-[:HAS_ACTIVITY]->(act:Activity)

        RETURN collect(
            DISTINCT act.name
        ) AS activities
    }

    CALL {
        WITH d

        MATCH (d)-[:OFFERS_FOOD]->(f:Food)

        RETURN collect(
            DISTINCT f.name
        ) AS food
    }

    RETURN
        d.name AS name,
        d.description AS description,
        d.category AS category,
        d.best_season AS best_season,
        d.latitude AS latitude,
        d.longitude AS longitude,
        d.image_url AS image_url,
        d.source_url AS source_url,
        attractions,
        activities,
        food
    """

    with app.state.neo4j_driver.session() as session:

        result = session.run(
            query,
            destination_id=destination_id,
        )

        record = result.single()

    if record is None:

        return {
            "status": "not_found",
            "message": "Destination not found",
        }

    return {
        "status": "success",
        "destination": dict(record),
    }


# ── Smart Itinerary API ─────────────────────────────────────────────────────

@app.post("/api/itinerary")
def create_itinerary(
    request: ItineraryRequest,
):
    """
    Generate a destination-level smart itinerary
    from a natural-language travel query.

    Example:

    "I have one day in Mysuru and want
     heritage and local food."
    """

    # 1. Validate query

    if not request.query or not request.query.strip():

        return {
            "status": "error",
            "message": "Please enter an itinerary request.",
            "preferences": None,
            "itinerary": None,
        }

    # 2. Parse natural-language requirements

    preferences = parse_query(
        request.query
    )

    destination_name = preferences.get(
        "location"
    )

    duration_days = (
        preferences.get("duration_days")
        or 1
    )

    interests = preferences.get(
        "interests",
        [],
    )

    food_preferences = preferences.get(
        "food_preferences",
        [],
    )

    # Destination is required.

    if not destination_name:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please specify a Karnataka destination."
            ),
        )

    # 3. Retrieve attractions

    query = """
    MATCH (d:Destination)

    WHERE toLower(d.name)
        = toLower($destination)

    OPTIONAL MATCH (d)-->(a:Attraction)

    RETURN
        d.name AS destination,

        collect(
            DISTINCT {
                name: a.name,
                attraction_type: a.attraction_type,
                description: a.description,
                latitude: a.latitude,
                longitude: a.longitude,
                opening_time: a.opening_time,
                closing_time: a.closing_time
            }
        ) AS attractions
    """

    with app.state.neo4j_driver.session() as session:

        result = session.run(
            query,
            destination=destination_name,
        )

        record = result.single()

    # Destination not found.

    if record is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Destination "
                f"'{destination_name}' "
                f"not found."
            ),
        )

    attractions = record[
        "attractions"
    ]

    # Remove empty Neo4j attraction objects.

    attractions = [
        attraction
        for attraction in attractions
        if attraction.get("name")
    ]

    # No attractions.

    if not attractions:

        raise HTTPException(
            status_code=404,
            detail=(
                f"No attractions found "
                f"for {destination_name}."
            ),
        )

    # 4. Generate itinerary

    itinerary = build_itinerary(
        attractions=attractions,
        duration_days=duration_days,
        interests=interests,
        food_preferences=food_preferences,
    )

    # 5. Return structured itinerary

    return {
        "status": "success",
        "query": request.query,
        "preferences": preferences,
        "destination": destination_name,
        "itinerary": itinerary,
    }