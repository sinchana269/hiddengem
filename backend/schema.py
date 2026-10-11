"""
HiddenGem – Neo4j Graph Schema
---------------------------------
This module defines:
  1. CONSTRAINTS  – guarantee uniqueness for each node label
  2. INDEXES      – speed up property lookups used in searches
  3. NODE helpers  – MERGE functions for each node type
  4. RELATIONSHIP helpers – MERGE functions for each relationship type

Why MERGE instead of CREATE?
  MERGE acts like "create if not exists".
  Running this module more than once will NOT create duplicate nodes.

Node labels in the graph
──────────────────────────────────────────────────────────────────────
  Destination   – a tourism location in Karnataka
  District      – an administrative district of Karnataka
  Attraction    – a specific attraction inside/near a Destination
  Activity      – a tourist activity at a Destination
  Food          – a local dish linked to a Destination
  Hashtag       – a social-media tag
  TravelContent – a blog post / reel / tweet about a Destination
  Review        – a traveller review of a Destination

Relationships
──────────────────────────────────────────────────────────────────────
  (Destination)-[:LOCATED_IN]  ->(District)
  (Destination)-[:HAS_PLACE]   ->(Attraction)
  (Destination)-[:HAS_ACTIVITY]->(Activity)
  (Destination)-[:OFFERS_FOOD] ->(Food)
  (Destination)-[:NEAR]        ->(Destination)
  (Destination)-[:HAS_HASHTAG] ->(Hashtag)
  (TravelContent)-[:MENTIONS]  ->(Destination)
  (TravelContent)-[:CONTAINS]  ->(Hashtag)
  (Review)-[:ABOUT]            ->(Destination)
"""

from neo4j import Driver
from models import (
    Destination, District, Attraction,
    Activity, Food, Hashtag, TravelContent, Review,
)


# ═══════════════════════════════════════════════════════════════════════
# 1. CONSTRAINTS & INDEXES
# ═══════════════════════════════════════════════════════════════════════

def create_constraints(driver: Driver) -> list[str]:
    """
    Create uniqueness constraints for every node label.
    Neo4j automatically creates a backing index for each constraint.

    Safe to call multiple times – Neo4j skips constraints that already exist.

    Returns a list of constraint names that were processed.
    """
    # Each tuple is (constraint_name, node_label, property)
    constraints = [
        ("unique_destination_name",    "Destination",   "name"),
        ("unique_district_name",       "District",      "name"),
        ("unique_attraction_name",     "Attraction",    "name"),
        ("unique_activity_name",       "Activity",      "name"),
        ("unique_food_name",           "Food",          "name"),
        ("unique_hashtag_tag",         "Hashtag",       "tag"),
        ("unique_travelcontent_url",   "TravelContent", "url"),
        ("unique_review_id",           "Review",        "review_id"),
    ]

    created = []
    with driver.session() as session:
        for constraint_name, label, prop in constraints:
            cypher = (
                f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS "
                f"FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE"
            )
            session.run(cypher)
            created.append(constraint_name)

    return created


def create_indexes(driver: Driver) -> list[str]:
    """
    Create extra indexes on properties that will be searched frequently.
    Uniqueness constraints already index their property, so we only
    add indexes for additional searchable properties here.

    Safe to call multiple times – IF NOT EXISTS prevents duplicates.
    """
    indexes = [
        # (index_name, label, property)
        ("idx_destination_category",  "Destination",   "category"),
        ("idx_destination_best_season","Destination",  "best_season"),
        ("idx_activity_type",         "Activity",      "activity_type"),
        ("idx_attraction_type",       "Attraction",    "attraction_type"),
        ("idx_review_rating",         "Review",        "rating"),
        ("idx_travelcontent_platform","TravelContent", "platform"),
    ]

    created = []
    with driver.session() as session:
        for index_name, label, prop in indexes:
            cypher = (
                f"CREATE INDEX {index_name} IF NOT EXISTS "
                f"FOR (n:{label}) ON (n.{prop})"
            )
            session.run(cypher)
            created.append(index_name)

    return created


# ═══════════════════════════════════════════════════════════════════════
# 2. NODE HELPERS  (MERGE = create if not exists)
# ═══════════════════════════════════════════════════════════════════════

def merge_destination(session, dest: Destination) -> None:
    """
    Create or update a Destination node.
    MERGE matches on 'name' (the unique key).
    ON CREATE SET writes properties only when the node is brand new.
    ON MATCH SET updates mutable properties if the node already exists.
    """
    session.run(
        """
        MERGE (d:Destination {name: $name})
        ON CREATE SET
            d.description = $description,
            d.category    = $category,
            d.latitude    = $latitude,
            d.longitude   = $longitude,
            d.best_season = $best_season,
            d.image_url   = $image_url
        ON MATCH SET
            d.description = $description,
            d.category    = $category,
            d.best_season = $best_season,
            d.image_url   = $image_url
        """,
        name=dest.name,
        description=dest.description,
        category=dest.category,
        latitude=dest.latitude,
        longitude=dest.longitude,
        best_season=dest.best_season,
        image_url=dest.image_url,
    )


def merge_district(session, district: District) -> None:
    """Create or match a District node."""
    session.run(
        "MERGE (d:District {name: $name})",
        name=district.name,
    )


def merge_attraction(session, attraction: Attraction) -> None:
    """Create or update an Attraction node with itinerary data."""

    session.run(
        """
        MERGE (a:Attraction {name: $name})

        ON CREATE SET
            a.attraction_type = $attraction_type,
            a.description = $description,
            a.latitude = $latitude,
            a.longitude = $longitude,
            a.opening_time = $opening_time,
            a.closing_time = $closing_time

        ON MATCH SET
            a.attraction_type = $attraction_type,
            a.description = $description,
            a.latitude = $latitude,
            a.longitude = $longitude,
            a.opening_time = $opening_time,
            a.closing_time = $closing_time
        """,

        name=attraction.name,
        attraction_type=attraction.attraction_type,
        description=attraction.description,
        latitude=attraction.latitude,
        longitude=attraction.longitude,
        opening_time=attraction.opening_time,
        closing_time=attraction.closing_time,
    )


def merge_activity(session, activity: Activity) -> None:
    """Create or update an Activity node."""
    session.run(
        """
        MERGE (a:Activity {name: $name})
        ON CREATE SET a.activity_type = $activity_type, a.difficulty = $difficulty
        ON MATCH  SET a.activity_type = $activity_type, a.difficulty = $difficulty
        """,
        name=activity.name,
        activity_type=activity.activity_type,
        difficulty=activity.difficulty,
    )


def merge_food(session, food: Food) -> None:
    """Create or update a Food node."""
    session.run(
        """
        MERGE (f:Food {name: $name})
        ON CREATE SET f.food_type = $food_type, f.is_vegetarian = $is_vegetarian
        ON MATCH  SET f.food_type = $food_type, f.is_vegetarian = $is_vegetarian
        """,
        name=food.name,
        food_type=food.food_type,
        is_vegetarian=food.is_vegetarian,
    )


def merge_hashtag(session, hashtag: Hashtag) -> None:
    """Create or match a Hashtag node. Tag stored without '#'."""
    session.run(
        "MERGE (h:Hashtag {tag: $tag})",
        tag=hashtag.tag,
    )


def merge_travel_content(session, content: TravelContent) -> None:
    """Create or update a TravelContent node."""
    session.run(
        """
        MERGE (tc:TravelContent {url: $url})
        ON CREATE SET tc.platform = $platform, tc.title = $title, tc.posted_at = $posted_at
        ON MATCH  SET tc.platform = $platform, tc.title = $title, tc.posted_at = $posted_at
        """,
        url=content.url,
        platform=content.platform,
        title=content.title,
        posted_at=content.posted_at,
    )


def merge_review(session, review: Review) -> None:
    """Create or update a Review node."""
    session.run(
        """
        MERGE (r:Review {review_id: $review_id})
        ON CREATE SET r.text = $text, r.rating = $rating,
                      r.author = $author, r.created_at = $created_at
        ON MATCH  SET r.text = $text, r.rating = $rating,
                      r.author = $author, r.created_at = $created_at
        """,
        review_id=review.review_id,
        text=review.text,
        rating=review.rating,
        author=review.author,
        created_at=review.created_at,
    )


# ═══════════════════════════════════════════════════════════════════════
# 3. RELATIONSHIP HELPERS  (MERGE = create if not exists)
# ═══════════════════════════════════════════════════════════════════════

def link_destination_to_district(session, dest_name: str, district_name: str) -> None:
    """(Destination)-[:LOCATED_IN]->(District)"""
    session.run(
        """
        MATCH (d:Destination {name: $dest_name})
        MATCH (dist:District {name: $district_name})
        MERGE (d)-[:LOCATED_IN]->(dist)
        """,
        dest_name=dest_name,
        district_name=district_name,
    )


def link_destination_to_attraction(session, dest_name: str, attraction_name: str) -> None:
    """(Destination)-[:HAS_PLACE]->(Attraction)"""
    session.run(
        """
        MATCH (d:Destination {name: $dest_name})
        MATCH (a:Attraction  {name: $attraction_name})
        MERGE (d)-[:HAS_PLACE]->(a)
        """,
        dest_name=dest_name,
        attraction_name=attraction_name,
    )


def link_destination_to_activity(session, dest_name: str, activity_name: str) -> None:
    """(Destination)-[:HAS_ACTIVITY]->(Activity)"""
    session.run(
        """
        MATCH (d:Destination {name: $dest_name})
        MATCH (a:Activity    {name: $activity_name})
        MERGE (d)-[:HAS_ACTIVITY]->(a)
        """,
        dest_name=dest_name,
        activity_name=activity_name,
    )


def link_destination_to_food(session, dest_name: str, food_name: str) -> None:
    """(Destination)-[:OFFERS_FOOD]->(Food)"""
    session.run(
        """
        MATCH (d:Destination {name: $dest_name})
        MATCH (f:Food        {name: $food_name})
        MERGE (d)-[:OFFERS_FOOD]->(f)
        """,
        dest_name=dest_name,
        food_name=food_name,
    )


def link_destinations_near(session, dest_a: str, dest_b: str) -> None:
    """(Destination)-[:NEAR]->(Destination)  — bidirectional convenience wrapper."""
    session.run(
        """
        MATCH (a:Destination {name: $dest_a})
        MATCH (b:Destination {name: $dest_b})
        MERGE (a)-[:NEAR]->(b)
        MERGE (b)-[:NEAR]->(a)
        """,
        dest_a=dest_a,
        dest_b=dest_b,
    )


def link_destination_to_hashtag(session, dest_name: str, tag: str) -> None:
    """(Destination)-[:HAS_HASHTAG]->(Hashtag)"""
    session.run(
        """
        MATCH (d:Destination {name: $dest_name})
        MATCH (h:Hashtag     {tag: $tag})
        MERGE (d)-[:HAS_HASHTAG]->(h)
        """,
        dest_name=dest_name,
        tag=tag,
    )


def link_content_mentions_destination(session, url: str, dest_name: str) -> None:
    """(TravelContent)-[:MENTIONS]->(Destination)"""
    session.run(
        """
        MATCH (tc:TravelContent {url: $url})
        MATCH (d:Destination    {name: $dest_name})
        MERGE (tc)-[:MENTIONS]->(d)
        """,
        url=url,
        dest_name=dest_name,
    )


def link_content_contains_hashtag(session, url: str, tag: str) -> None:
    """(TravelContent)-[:CONTAINS]->(Hashtag)"""
    session.run(
        """
        MATCH (tc:TravelContent {url: $url})
        MATCH (h:Hashtag        {tag: $tag})
        MERGE (tc)-[:CONTAINS]->(h)
        """,
        url=url,
        tag=tag,
    )


def link_review_about_destination(session, review_id: str, dest_name: str) -> None:
    """(Review)-[:ABOUT]->(Destination)"""
    session.run(
        """
        MATCH (r:Review      {review_id: $review_id})
        MATCH (d:Destination {name: $dest_name})
        MERGE (r)-[:ABOUT]->(d)
        """,
        review_id=review_id,
        dest_name=dest_name,
    )


# ═══════════════════════════════════════════════════════════════════════
# 4. TOP-LEVEL INITIALISER
# ═══════════════════════════════════════════════════════════════════════

def initialise_schema(driver: Driver) -> dict:
    """
    Run constraint + index setup in one call.
    Called from the /api/schema/init endpoint.

    Returns a summary dict for the API response.
    """
    constraints = create_constraints(driver)
    indexes     = create_indexes(driver)
    return {
        "status":      "schema initialised",
        "constraints": constraints,
        "indexes":     indexes,
    }
