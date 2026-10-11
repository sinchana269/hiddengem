
"""
HiddenGem - Natural Language Query Parser

Uses:
- spaCy for basic NLP processing
- Regex for duration and budget extraction
- Keyword dictionaries for tourism preference extraction

The parser does NOT use any external AI/LLM API.
"""

import re
from typing import Dict, List, Optional

import spacy


# ---------------------------------------------------------
# spaCy model
# ---------------------------------------------------------

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = spacy.blank("en")


# ---------------------------------------------------------
# Keyword dictionaries
# ---------------------------------------------------------

INTEREST_KEYWORDS = {
    "nature": [
        "nature",
        "natural",
        "forest",
        "forests",
        "greenery",
        "scenic",
        "landscape",
    ],
    "wildlife": [
        "wildlife",
        "animals",
        "safari",
        "birds",
        "bird watching",
        "birdwatching",
    ],
    "heritage": [
        "heritage",
        "historical",
        "history",
        "historic",
        "monument",
        "monuments",
        "architecture",
        "ancient",
    ],
    "beach": [
        "beach",
        "beaches",
        "coast",
        "coastal",
        "sea",
        "seaside",
    ],
    "waterfalls": [
        "waterfall",
        "waterfalls",
        "falls",
    ],
    "photography": [
        "photography",
        "photograph",
        "photographs",
        "photos",
        "photo",
        "sunrise",
        "sunset",
    ],
    "spiritual": [
        "spiritual",
        "temple",
        "temples",
        "pilgrimage",
        "religious",
    ],
}


ACTIVITY_KEYWORDS = {
    "trekking": [
        "trek",
        "trekking",
        "hiking",
        "hike",
    ],
    "rafting": [
        "rafting",
        "raft",
    ],
    "camping": [
        "camping",
        "camp",
    ],
    "boating": [
        "boating",
        "boat",
        "kayaking",
        "kayak",
    ],
    "cycling": [
        "cycling",
        "cycle",
        "biking",
        "bike",
    ],
    "wildlife": [
        "safari",
        "wildlife safari",
        "bird watching",
        "birdwatching",
    ],
    "photography": [
        "photography",
        "photograph",
        "photos",
    ],
    "heritage": [
        "heritage walk",
        "heritage tour",
    ],
}


TRAVEL_STYLE_KEYWORDS = {
    "peaceful": [
        "peaceful",
        "peace",
        "quiet",
        "calm",
        "relaxing",
        "relaxed",
        "tranquil",
    ],
    "adventure": [
        "adventure",
        "adventurous",
        "thrilling",
        "thrill",
        "exciting",
    ],
    "romantic": [
        "romantic",
        "romance",
        "couple",
    ],
    "luxury": [
        "luxury",
        "luxurious",
        "premium",
    ],
    "budget": [
        "budget",
        "cheap",
        "affordable",
        "economical",
    ],
}


FOOD_KEYWORDS = {
    "vegetarian food": [
        "vegetarian",
        "veg",
    ],
    "non-vegetarian food": [
        "non vegetarian",
        "non-vegetarian",
        "nonveg",
        "non-veg",
    ],
    "local food": [
        "local food",
        "local cuisine",
        "local dishes",
        "traditional food",
        "traditional cuisine",
    ],
    "south indian food": [
        "south indian",
        "south indian food",
    ],
}


TRIP_TYPE_KEYWORDS = {
    "road_trip": [
        "road trip",
        "roadtrip",
        "drive",
        "driving trip",
    ],
    "weekend": [
        "weekend",
    ],
    "day_trip": [
        "day trip",
        "one day trip",
        "one-day trip",
        "same day",
        "same-day",
    ],
}


GROUP_TYPE_KEYWORDS = {
    "friends": [
        "friends",
        "friend group",
        "group of friends",
    ],
    "family": [
        "family",
        "parents",
        "children",
        "kids",
    ],
    "couple": [
        "couple",
        "partner",
        "husband",
        "wife",
    ],
    "solo": [
        "solo",
        "alone",
        "by myself",
    ],
}


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalize text for NLP processing.

    The original user query is never modified.

    Commas are preserved because they may belong to
    formatted numbers such as:

        ₹4,000
        ₹40,000
        ₹1,00,000
    """

    text = text.lower().strip()

    # Normalize Unicode punctuation
    text = text.replace("–", "-")
    text = text.replace("—", "-")

    # Replace punctuation with spaces.
    #
    # IMPORTANT:
    # Commas are intentionally NOT removed here because
    # commas may be part of a formatted budget.
    text = re.sub(
        r"[.;:!?()\[\]{}\"']",
        " ",
        text,
    )

    # Collapse repeated whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def contains_keyword(text: str, keyword: str) -> bool:
    """
    Safely check whether a keyword occurs as a complete
    word or phrase.
    """

    keyword = keyword.lower().strip()

    pattern = (
        r"(?<!\w)"
        + re.escape(keyword)
        + r"(?!\w)"
    )

    return bool(
        re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )
    )


def extract_keyword_matches(
    text: str,
    keyword_dictionary: Dict[str, List[str]],
) -> List[str]:
    """
    Extract matching categories from a keyword dictionary.
    """

    matches = []

    for category, keywords in keyword_dictionary.items():

        for keyword in keywords:

            if contains_keyword(text, keyword):
                matches.append(category)
                break

    return matches


# ---------------------------------------------------------
# Location extraction
# ---------------------------------------------------------

KARNATAKA_LOCATIONS = [
    "mysuru",
    "mysore",
    "bengaluru",
    "bangalore",
    "coorg",
    "kodagu",
    "chikkamagaluru",
    "chikmagalur",
    "hampi",
    "udupi",
    "mangaluru",
    "mangalore",
    "shivamogga",
    "shimoga",
    "kabini",
    "bandipur",
    "sakleshpur",
    "gokarna",
    "karwar",
    "madikeri",
    "belur",
    "halebidu",
    "badami",
    "vijayapura",
    "bijapur",
    "davangere",
    "hassan",
]


LOCATION_NORMALIZATION = {
    "mysore": "Mysuru",
    "bangalore": "Bengaluru",
    "chikmagalur": "Chikkamagaluru",
    "mangalore": "Mangaluru",
    "shimoga": "Shivamogga",
    "bijapur": "Vijayapura",
}


def extract_location(text: str) -> Optional[str]:
    """
    Extract a known Karnataka location from the query.
    """

    for location in KARNATAKA_LOCATIONS:

        if contains_keyword(text, location):

            if location in LOCATION_NORMALIZATION:
                return LOCATION_NORMALIZATION[location]

            return location.title()

    return None


# ---------------------------------------------------------
# Duration extraction
# ---------------------------------------------------------

def extract_duration(text: str) -> Optional[int]:
    """
    Extract duration in days.

    Examples:

        '2 day trip' -> 2
        '3 days' -> 3
        '2-day trip' -> 2
        'one day trip' -> 1
        'day trip' -> 1
        'same day' -> 1
        'weekend trip' -> None
    """

    # Numeric duration:
    #
    # 2 day
    # 2 days
    # 2-day
    # 2-days
    #
    match = re.search(
        r"\b(\d+)\s*[-]?\s*days?\b",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        return int(match.group(1))

    # Explicit one-day wording
    if contains_keyword(text, "one day"):
        return 1

    if contains_keyword(text, "day trip"):
        return 1

    if contains_keyword(text, "same day"):
        return 1

    return None


# ---------------------------------------------------------
# Budget extraction
# ---------------------------------------------------------

def extract_budget(text: str) -> Optional[int]:
    """
    Extract maximum budget from natural language.

    Supports:

        ₹4000
        ₹4,000
        ₹ 4,000
        ₹1,00,000

        Rs 4000
        Rs. 4,000

        INR 4000

        under 4000
        below ₹5,000
        within Rs 10000
        up to ₹10,000
        maximum 15000

    The original query is never modified.

    No query-specific or destination-specific hardcoding
    is used.
    """

    # -----------------------------------------------------
    # Create a temporary parsing copy.
    #
    # Commas are removed ONLY here so that:
    #
    # ₹4,000 -> ₹4000
    #
    # The original input remains untouched.
    # -----------------------------------------------------

    clean = text.replace(",", "")

    # -----------------------------------------------------
    # Currency followed by amount
    #
    # Examples:
    # ₹4000
    # ₹ 4000
    # Rs 4000
    # Rs. 4000
    # INR 4000
    # -----------------------------------------------------

    currency_pattern = re.search(
        r"(?:₹|rs\.?|inr)"
        r"\s*"
        r"(\d+(?:\.\d+)?)",
        clean,
        flags=re.IGNORECASE,
    )

    if currency_pattern:

        amount = float(
            currency_pattern.group(1)
        )

        return int(amount)

    # -----------------------------------------------------
    # Budget limit expressions
    #
    # Examples:
    # under 4000
    # below ₹5000
    # within Rs 10000
    # maximum 15000
    # max ₹20000
    # upto 8000
    # up to ₹10000
    # -----------------------------------------------------

    limit_pattern = re.search(
        r"(?:"
        r"under|"
        r"below|"
        r"within|"
        r"maximum|"
        r"max|"
        r"upto|"
        r"up to"
        r")"
        r"\s*"
        r"(?:₹|rs\.?|inr)?"
        r"\s*"
        r"(\d+(?:\.\d+)?)",
        clean,
        flags=re.IGNORECASE,
    )

    if limit_pattern:

        amount = float(
            limit_pattern.group(1)
        )

        return int(amount)

    return None


# ---------------------------------------------------------
# Main parser
# ---------------------------------------------------------

def parse_query(query: str) -> Dict:
    """
    Parse a natural-language tourism query.

    Returns:

        {
            "original_query": str,
            "location": Optional[str],
            "duration_days": Optional[int],
            "budget": Optional[int],
            "interests": List[str],
            "activities": List[str],
            "travel_style": List[str],
            "food_preferences": List[str],
            "trip_type": List[str],
            "group_type": List[str]
        }
    """

    # -----------------------------------------------------
    # Empty input
    # -----------------------------------------------------

    if not query or not query.strip():

        return {
            "original_query": query,
            "location": None,
            "duration_days": None,
            "budget": None,
            "interests": [],
            "activities": [],
            "travel_style": [],
            "food_preferences": [],
            "trip_type": [],
            "group_type": [],
        }

    # -----------------------------------------------------
    # IMPORTANT:
    #
    # Preserve the exact original user input.
    # Never normalize or modify this value.
    # -----------------------------------------------------

    original_query = query

    # -----------------------------------------------------
    # Create a separate normalized copy for NLP.
    # -----------------------------------------------------

    text = normalize_text(query)

    # -----------------------------------------------------
    # spaCy processing
    # -----------------------------------------------------

    doc = nlp(text)

    # The current parser uses deterministic rules and
    # keyword dictionaries. spaCy processing is retained
    # for NLP preprocessing and future expansion.
    _ = doc

    # -----------------------------------------------------
    # Extract structured preferences
    # -----------------------------------------------------

    location = extract_location(text)

    duration_days = extract_duration(text)

    budget = extract_budget(text)

    interests = extract_keyword_matches(
        text,
        INTEREST_KEYWORDS,
    )

    activities = extract_keyword_matches(
        text,
        ACTIVITY_KEYWORDS,
    )

    travel_style = extract_keyword_matches(
        text,
        TRAVEL_STYLE_KEYWORDS,
    )

    food_preferences = extract_keyword_matches(
        text,
        FOOD_KEYWORDS,
    )

    trip_type = extract_keyword_matches(
        text,
        TRIP_TYPE_KEYWORDS,
    )

    group_type = extract_keyword_matches(
        text,
        GROUP_TYPE_KEYWORDS,
    )

    # -----------------------------------------------------
    # Cleanup / conflict handling
    # -----------------------------------------------------

    # A numeric duration greater than one day should never
    # automatically become a day trip.
    #
    # Example:
    #
    # 2-day trip -> duration_days = 2
    #               trip_type does not contain day_trip
    #
    if duration_days is not None and duration_days > 1:

        trip_type = [
            item
            for item in trip_type
            if item != "day_trip"
        ]

    # -----------------------------------------------------
    # Wildlife
    #
    # Wildlife is treated as an interest.
    # Safari remains an activity.
    # -----------------------------------------------------

    if "wildlife" in activities:
        activities.remove("wildlife")

    # -----------------------------------------------------
    # Heritage
    #
    # General "heritage" is an interest.
    #
    # "heritage walk" / "heritage tour" can be activities.
    # -----------------------------------------------------

    if "heritage" in activities:

        if not (
            contains_keyword(
                text,
                "heritage walk",
            )
            or contains_keyword(
                text,
                "heritage tour",
            )
        ):

            activities.remove("heritage")

    # -----------------------------------------------------
    # Photography
    #
    # Photography is treated as an interest.
    # -----------------------------------------------------

    if "photography" in activities:
        activities.remove("photography")

    # -----------------------------------------------------
    # Nature
    #
    # Nature is an interest, not a travel style.
    # -----------------------------------------------------

    if "nature" in travel_style:
        travel_style.remove("nature")

    # -----------------------------------------------------
    # Remove duplicates while preserving order.
    # -----------------------------------------------------

    interests = list(
        dict.fromkeys(interests)
    )

    activities = list(
        dict.fromkeys(activities)
    )

    travel_style = list(
        dict.fromkeys(travel_style)
    )

    food_preferences = list(
        dict.fromkeys(food_preferences)
    )

    trip_type = list(
        dict.fromkeys(trip_type)
    )

    group_type = list(
        dict.fromkeys(group_type)
    )

    # -----------------------------------------------------
    # Final structured result
    # -----------------------------------------------------

    return {
        "original_query": original_query,
        "location": location,
        "duration_days": duration_days,
        "budget": budget,
        "interests": interests,
        "activities": activities,
        "travel_style": travel_style,
        "food_preferences": food_preferences,
        "trip_type": trip_type,
        "group_type": group_type,
    }


# ---------------------------------------------------------
# Manual testing
# ---------------------------------------------------------
if __name__ == "__main__":

    test_queries = [
        "I want a peaceful 2-day trip from Mysuru with waterfalls and local food under ₹4,000",
        "I want an adventure trip with rafting and wildlife",
        "Suggest a 3 day heritage trip",
        "I want a quiet nature trip",
        "Plan a weekend road trip with friends for photography and trekking",
        "I want a romantic trip with my partner and local vegetarian food",
    ]

    print("=" * 60)
    print("HiddenGem NLP Query Parser Test")
    print("=" * 60)

    for query in test_queries:

        print("\n" + "=" * 60)
        print("QUERY:")
        print(query)
        print("RAW INPUT:", repr(query))

        parsed = parse_query(query)

        print("\nPARSED:")

        for key, value in parsed.items():
            print(f"{key}: {value}")