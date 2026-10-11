"""
HiddenGem – Neo4j Data Import
---------------------------------
Imports the cleaned Karnataka Tourism dataset into Neo4j.

Project scope:
- Exactly 5 Karnataka destinations
- Source-grounded tourism data
- No invented district/category/location data
- Destination description, image and source URL are preserved
- Cleans obvious section headings before creating graph nodes
"""

import json
import re
from pathlib import Path

from database import get_driver, close_driver
from models import Destination, Attraction, Activity, Food
from schema import (
    initialise_schema,
    merge_destination,
    merge_attraction,
    merge_activity,
    merge_food,
    link_destination_to_attraction,
    link_destination_to_activity,
    link_destination_to_food,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = (
    BASE_DIR
    / "data"
    / "cleaned"
    / "scraped_destinations.json"
)


# ---------------------------------------------------------------------
# Destination naming
# ---------------------------------------------------------------------

DESTINATION_NAMES = {
    "mysuru": "Mysuru",
    "coorg": "Coorg",
    "hampi": "Hampi",
    "jog-falls": "Jog Falls",
    "dandeli": "Dandeli",
}


# ---------------------------------------------------------------------
# Known section headings that should NOT become Attraction nodes.
# These are filtering rules, not invented tourism facts.
# ---------------------------------------------------------------------

INVALID_ATTRACTIONS = {
    "waterfall viewing & photography",
    "jog falls nearby places",
    "history & significance of jog falls",
    "the four cascades of jog falls",
    "viewpoints at jog falls",
    "main viewing deck (front panoramic viewpoint)",
    "british bungalow viewpoint",
    "badami cave temples",
    "lalitha mahal palace hotel",
    "the light and sound show at mysuru palace",
}


# ---------------------------------------------------------------------
# Known generic headings that should NOT become Food nodes.
# ---------------------------------------------------------------------

INVALID_FOOD = {
    "food",
    "culinary",
    "cuisine",
    "local food",
    "food & culinary",
    "where to try coorg food",
    "what food is coorg known for?",
}


# ---------------------------------------------------------------------
# Dandeli correction
# ---------------------------------------------------------------------

DANDELI_ATTRACTION = "Dandeli Wildlife Sanctuary"


# ---------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------

def clean_name(value):
    """Normalize whitespace and remove surrounding separators."""

    if not value:
        return ""

    value = re.sub(
        r"\s+",
        " ",
        str(value),
    )

    return value.strip(
        " -–—:|"
    )


def unique_clean(items):
    """Remove empty values and case-insensitive duplicates."""

    result = []
    seen = set()

    for item in items or []:

        item = clean_name(item)

        if not item:
            continue

        key = item.casefold()

        if key not in seen:

            seen.add(key)
            result.append(item)

    return result


# ---------------------------------------------------------------------
# Description
# ---------------------------------------------------------------------

def extract_description(record):
    """
    Prefer the cleaned description.

    The cleaner already determines the best source-grounded
    description, so we use that first.

    Fallback:
    1. meta description
    2. first reasonably long paragraph
    """

    description = clean_name(
        record.get(
            "description",
            "",
        )
    )

    if description:
        return description

    meta = clean_name(
        record.get(
            "meta_desc",
            "",
        )
    )

    if meta:
        return meta

    for paragraph in record.get(
        "paragraphs",
        [],
    ):

        paragraph = clean_name(
            paragraph
        )

        if len(paragraph) >= 80:
            return paragraph

    return ""


# ---------------------------------------------------------------------
# Primary image
# ---------------------------------------------------------------------

def extract_primary_image(record):
    """
    Use the primary image selected by the cleaner.

    Removes accidental whitespace inside scraped image URLs.
    Falls back to the first image if necessary.
    """

    primary_image = record.get(
        "primary_image",
        "",
    )

    if primary_image:
        # Remove whitespace accidentally introduced into the URL.
        primary_image = re.sub(
            r"\s+",
            "",
            str(primary_image),
        ).strip()

    if primary_image:
        return primary_image

    images = record.get(
        "images",
        [],
    )

    for image in images:

        if isinstance(
            image,
            dict,
        ):

            url = image.get(
                "url",
                "",
            )

            if url:
                url = re.sub(
                    r"\s+",
                    "",
                    str(url),
                ).strip()

            if url:
                return url

        elif isinstance(
            image,
            str,
        ):

            url = re.sub(
                r"\s+",
                "",
                image,
            ).strip()

            if url:
                return url

    return ""

# ---------------------------------------------------------------------
# Best time
# ---------------------------------------------------------------------

def extract_best_season(record):
    """
    Extract a simple best-time value from source-derived sections.

    This does not invent a season when the source doesn't provide one.
    """

    sections = unique_clean(
        record.get(
            "best_time_sections",
            [],
        )
    )

    if not sections:
        return ""

    text = " ".join(
        sections
    )

    month_pattern = (
        r"\b("
        r"January|February|March|April|May|June|July|August|September|"
        r"October|November|December"
        r")\b"
    )

    months = re.findall(
        month_pattern,
        text,
        flags=re.IGNORECASE,
    )

    if months:

        result = []
        seen = set()

        for month in months:

            key = month.casefold()

            if key not in seen:

                seen.add(key)
                result.append(month)

        return ", ".join(result)

    return sections[0]


# ---------------------------------------------------------------------
# Attraction filtering
# ---------------------------------------------------------------------

def filter_attractions(items):

    result = []

    for item in unique_clean(
        items
    ):

        key = item.casefold()

        if key in INVALID_ATTRACTIONS:
            continue

        if "?" in item:
            continue

        result.append(item)

    return result


# ---------------------------------------------------------------------
# Activity filtering
# ---------------------------------------------------------------------

def filter_activities(items):

    result = []

    for item in unique_clean(
        items
    ):

        if "?" in item:
            continue

        result.append(item)

    return result


# ---------------------------------------------------------------------
# Food filtering
# ---------------------------------------------------------------------

def filter_food(items):

    result = []

    for item in unique_clean(
        items
    ):

        key = item.casefold()

        if key in INVALID_FOOD:
            continue

        if "?" in item:
            continue

        result.append(item)

    return result


# ---------------------------------------------------------------------
# Destination metadata update
# ---------------------------------------------------------------------

def update_destination_metadata(
    tx,
    destination_name,
    source_url,
):
    """
    Store the official Karnataka Tourism source URL.

    This is kept separate from the Destination model so we do not
    need to invent or change model fields just for the source link.
    """

    tx.run(
        """
        MATCH (d:Destination)
        WHERE d.name = $destination_name
        SET d.source_url = $source_url
        """,
        destination_name=destination_name,
        source_url=source_url,
    ).consume()


# ---------------------------------------------------------------------
# Import one destination
# ---------------------------------------------------------------------

def import_destination(
    tx,
    record,
):

    slug = clean_name(
        record.get(
            "slug",
            "",
        )
    )

    source_url = clean_name(
        record.get(
            "source_url",
            "",
        )
    )

    name = DESTINATION_NAMES.get(
        slug,
        clean_name(
            record.get(
                "page_title",
                "",
            )
        ),
    )

    description = extract_description(
        record
    )

    primary_image = extract_primary_image(
        record
    )

    best_season = extract_best_season(
        record
    )

    attractions = filter_attractions(
        record.get(
            "attractions_sections",
            [],
        )
    )

    activities = filter_activities(
        record.get(
            "activities_sections",
            [],
        )
    )

    food = filter_food(
        record.get(
            "food_sections",
            [],
        )
    )

    # -------------------------------------------------------------
    # Dandeli correction
    # -------------------------------------------------------------

    if slug == "dandeli":

        activities = [
            item
            for item in activities
            if item.casefold()
            != DANDELI_ATTRACTION.casefold()
        ]

        if DANDELI_ATTRACTION.casefold() not in {
            item.casefold()
            for item in attractions
        }:

            attractions.append(
                DANDELI_ATTRACTION
            )

    # -------------------------------------------------------------
    # Destination node
    # -------------------------------------------------------------

    destination = Destination(
        name=name,
        description=description,
        category="",
        latitude=0.0,
        longitude=0.0,
        best_season=best_season,
        image_url=primary_image,
    )

    merge_destination(
        tx,
        destination,
    )

    # -------------------------------------------------------------
    # Official source URL
    # -------------------------------------------------------------

    update_destination_metadata(
        tx,
        destination_name=name,
        source_url=source_url,
    )

    # -------------------------------------------------------------
    # Attraction nodes + relationships
    # -------------------------------------------------------------

    for attraction_name in attractions:

        attraction = Attraction(
            name=attraction_name,
            attraction_type="",
            description="",
        )

        merge_attraction(
            tx,
            attraction,
        )

        link_destination_to_attraction(
            tx,
            dest_name=name,
            attraction_name=attraction_name,
        )

    # -------------------------------------------------------------
    # Activity nodes + relationships
    # -------------------------------------------------------------

    for activity_name in activities:

        activity = Activity(
            name=activity_name,
            activity_type="",
            difficulty="",
        )

        merge_activity(
            tx,
            activity,
        )

        link_destination_to_activity(
            tx,
            dest_name=name,
            activity_name=activity_name,
        )

    # -------------------------------------------------------------
    # Food nodes + relationships
    # -------------------------------------------------------------

    for food_name in food:

        food_item = Food(
            name=food_name,
            food_type="",
            is_vegetarian=True,
        )

        merge_food(
            tx,
            food_item,
        )

        link_destination_to_food(
            tx,
            dest_name=name,
            food_name=food_name,
        )

    return {
        "name": name,
        "attractions": len(
            attractions
        ),
        "activities": len(
            activities
        ),
        "food": len(
            food
        ),
        "description": bool(
            description
        ),
        "image": bool(
            primary_image
        ),
        "source_url": source_url,
    }


# ---------------------------------------------------------------------
# Clear existing project graph
# ---------------------------------------------------------------------

def clear_project_graph(driver):

    """
    Clear the current HiddenGem graph before a controlled re-import.

    This is intentional because earlier imports may contain stale
    nodes from previous cleaner versions.
    """

    with driver.session() as session:

        session.run(
            """
            MATCH (n)
            DETACH DELETE n
            """
        ).consume()


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main():

    print(
        "HiddenGem – Neo4j Data Import"
    )

    print(
        "=" * 45
    )

    # -------------------------------------------------------------
    # Check data file
    # -------------------------------------------------------------

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"Cleaned data file not found:\n"
            f"{DATA_FILE}"
        )

    with open(
        DATA_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        records = json.load(
            file
        )

    if not isinstance(
        records,
        list,
    ):

        raise ValueError(
            "scraped_destinations.json "
            "must contain a list."
        )

    # Exactly five destinations are required.
    if len(records) != 5:

        raise ValueError(
            f"Expected exactly 5 destinations, "
            f"found {len(records)}."
        )

    # -------------------------------------------------------------
    # Neo4j connection
    # -------------------------------------------------------------

    driver = get_driver()

    try:

        print(
            "\nChecking Neo4j connection..."
        )

        driver.verify_connectivity()

        print(
            "Neo4j connected."
        )

        # ---------------------------------------------------------
        # Schema
        # ---------------------------------------------------------

        print(
            "\nInitialising schema..."
        )

        schema_result = initialise_schema(
            driver
        )

        print(
            schema_result
        )

        # ---------------------------------------------------------
        # Clear old graph
        # ---------------------------------------------------------

        print(
            "\nClearing previous HiddenGem graph..."
        )

        clear_project_graph(
            driver
        )

        print(
            "Previous graph cleared."
        )

        # ---------------------------------------------------------
        # Import
        # ---------------------------------------------------------

        print(
            "\nImporting destinations..."
        )

        print(
            "-" * 45
        )

        imported = []

        with driver.session() as session:

            for record in records:

                result = session.execute_write(
                    import_destination,
                    record,
                )

                imported.append(
                    result
                )

                print(
                    f"Imported: {result['name']} | "
                    f"attractions={result['attractions']} | "
                    f"activities={result['activities']} | "
                    f"food={result['food']} | "
                    f"description={'YES' if result['description'] else 'NO'} | "
                    f"image={'YES' if result['image'] else 'NO'}"
                )

        # ---------------------------------------------------------
        # Summary
        # ---------------------------------------------------------

        print(
            "\n" + "=" * 45
        )

        print(
            "Import complete."
        )

        print(
            "=" * 45
        )

        with driver.session() as session:

            result = session.run(
                """
                MATCH (n)
                RETURN labels(n)[0] AS label,
                       count(n) AS count
                ORDER BY label
                """
            )

            print(
                "\nNeo4j node counts:"
            )

            for row in result:

                print(
                    f"  {row['label']}: "
                    f"{row['count']}"
                )

            print(
                "\nDestination metadata:"
            )

            result = session.run(
                """
                MATCH (d:Destination)
                RETURN d.name AS name,
                       d.description AS description,
                       d.image_url AS image_url,
                       d.source_url AS source_url,
                       d.best_season AS best_season
                ORDER BY d.name
                """
            )

            for row in result:

                print(
                    f"\n  {row['name']}"
                )

                print(
                    f"    Description: "
                    f"{'YES' if row['description'] else 'NO'}"
                )

                print(
                    f"    Image: "
                    f"{'YES' if row['image_url'] else 'NO'}"
                )

                print(
                    f"    Source URL: "
                    f"{'YES' if row['source_url'] else 'NO'}"
                )

                print(
                    f"    Best season: "
                    f"{row['best_season'] or 'NOT AVAILABLE'}"
                )

    finally:

        close_driver(
            driver
        )


if __name__ == "__main__":

    main()