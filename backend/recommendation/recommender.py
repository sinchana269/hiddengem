"""
HiddenGem - Destination Recommendation Engine

Uses:
1. Deterministic weighted preference scoring.
2. TF-IDF + cosine similarity for content-based NLP matching.

Only supplied preference dimensions are considered.

No external AI/LLM API is used.
"""

from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_WEIGHTS = {
    "interest": 25,
    "activity": 20,
    "location": 20,
    "duration": 15,
    "budget": 10,
    "food": 10,
}


# -------------------------------------------------------------------
# Semantic keyword support
# -------------------------------------------------------------------

INTEREST_KEYWORDS = {
    "photography": [
        "photography",
        "viewpoint",
        "viewpoints",
        "scenic",
        "scenery",
        "landscape",
        "plantation",
        "palace",
        "temple",
        "lake",
        "waterfall",
        "wildlife",
        "ruins",
    ],
    "nature": [
        "nature",
        "forest",
        "plantation",
        "lake",
        "waterfall",
        "wildlife",
        "scenic",
    ],
    "waterfalls": [
        "waterfall",
        "waterfalls",
        "falls",
        "cascade",
    ],
    "wildlife": [
        "wildlife",
        "sanctuary",
        "national park",
        "forest",
        "animals",
        "bird",
        "bear",
    ],
    "heritage": [
        "heritage",
        "history",
        "historical",
        "temple",
        "palace",
        "fort",
        "monument",
        "ruins",
        "unesco",
    ],
    "spiritual": [
        "temple",
        "monastery",
        "church",
        "mosque",
        "spiritual",
        "pilgrimage",
    ],
}


# -------------------------------------------------------------------
# Basic helpers
# -------------------------------------------------------------------

def _to_list(value: Any) -> List[str]:
    """Convert a value into a clean list of strings."""

    if value is None:
        return []

    if isinstance(value, str):

        value = value.strip()

        if not value:
            return []

        return [value.lower()]

    if isinstance(value, list):

        return [
            str(item).strip().lower()
            for item in value
            if str(item).strip()
        ]

    return []


def _text(value: Any) -> str:
    """Convert a value to lowercase text."""

    if value is None:
        return ""

    return str(value).strip().lower()


def _matches_any(
    preferences: List[str],
    destination_values: List[str],
) -> bool:
    """Check exact or substring compatibility."""

    if not preferences or not destination_values:
        return False

    for preference in preferences:

        for destination_value in destination_values:

            if (
                preference == destination_value
                or preference in destination_value
                or destination_value in preference
            ):
                return True

    return False


def _contains_keyword(
    preference: str,
    destination_text: str,
) -> bool:
    """
    Check whether a preference is represented by
    source-grounded destination keywords.
    """

    keywords = INTEREST_KEYWORDS.get(
        preference,
        [preference],
    )

    return any(
        keyword in destination_text
        for keyword in keywords
    )


# -------------------------------------------------------------------
# Content preparation for TF-IDF
# -------------------------------------------------------------------

def _destination_text(
    destination: Dict[str, Any],
) -> str:
    """
    Build searchable text from actual destination data.
    """

    parts = []

    fields = [
        "name",
        "description",
        "category",
        "best_season",
        "location",
        "district",
    ]

    for field in fields:

        value = destination.get(field)

        if value:
            parts.append(str(value))

    for field in [
        "interests",
        "activities",
        "attractions",
        "food",
    ]:

        values = _to_list(
            destination.get(field)
        )

        parts.extend(values)

    return " ".join(parts).lower()


def _preference_text(
    preferences: Dict[str, Any],
) -> str:
    """
    Convert extracted user preferences into searchable text.
    """

    parts = []

    for field in [
        "location",
        "interests",
        "activities",
        "travel_style",
        "food_preferences",
        "trip_type",
        "group_type",
    ]:

        value = preferences.get(field)

        if isinstance(value, list):

            parts.extend(
                str(item).lower()
                for item in value
                if str(item).strip()
            )

        elif value:

            parts.append(
                str(value).lower()
            )

    return " ".join(parts)


def calculate_content_similarity(
    preferences: Dict[str, Any],
    destinations: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Calculate TF-IDF cosine similarity.

    Returns scores from 0 to 100.
    """

    if not destinations:
        return {}

    user_text = _preference_text(
        preferences
    )

    if not user_text.strip():

        return {
            destination.get("name", ""): 0.0
            for destination in destinations
        }

    destination_texts = [
        _destination_text(destination)
        for destination in destinations
    ]

    documents = [
        user_text,
        *destination_texts,
    ]

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    try:

        matrix = vectorizer.fit_transform(
            documents
        )

    except ValueError:

        return {
            destination.get("name", ""): 0.0
            for destination in destinations
        }

    similarities = cosine_similarity(
        matrix[0:1],
        matrix[1:],
    )[0]

    return {
        destinations[index].get("name", ""): round(
            float(similarities[index]) * 100,
            2,
        )
        for index in range(
            len(destinations)
        )
    }


# -------------------------------------------------------------------
# Interest matching
# -------------------------------------------------------------------

def _interest_match(
    preferences: Dict[str, Any],
    destination: Dict[str, Any],
) -> bool:
    """
    Check interest compatibility using actual
    destination content.
    """

    user_interests = _to_list(
        preferences.get("interests")
    )

    if not user_interests:
        return False

    destination_values = []

    destination_values.extend(
        _to_list(
            destination.get("interests")
        )
    )

    destination_values.extend(
        _to_list(
            destination.get("category")
        )
    )

    destination_values.extend(
        _to_list(
            destination.get("description")
        )
    )

    destination_values.extend(
        _to_list(
            destination.get("attractions")
        )
    )

    destination_values.extend(
        _to_list(
            destination.get("activities")
        )
    )

    destination_values.extend(
        _to_list(
            destination.get("food")
        )
    )

    destination_text = " ".join(
        destination_values
    )

    for preference in user_interests:

        if _matches_any(
            [preference],
            destination_values,
        ):
            return True

        if _contains_keyword(
            preference,
            destination_text,
        ):
            return True

    return False


# -------------------------------------------------------------------
# Activity matching
# -------------------------------------------------------------------

def _activity_match(
    preferences: Dict[str, Any],
    destination: Dict[str, Any],
) -> bool:
    """Check activity compatibility."""

    user_activities = _to_list(
        preferences.get("activities")
    )

    destination_activities = _to_list(
        destination.get("activities")
    )

    return _matches_any(
        user_activities,
        destination_activities,
    )


# -------------------------------------------------------------------
# Food matching
# -------------------------------------------------------------------

def _food_match(
    preferences: Dict[str, Any],
    destination: Dict[str, Any],
) -> bool:
    """
    Match food preferences using actual food data.

    'local food' means the destination has source-grounded
    local food information.

    More specific food preferences require actual
    destination food data to match.
    """

    user_food = _to_list(
        preferences.get("food_preferences")
    )

    if not user_food:
        return False

    destination_food = _to_list(
        destination.get("food")
    )

    if not destination_food:
        return False

    destination_text = " ".join(
        destination_food
    )

    for preference in user_food:

        # General local-food intent.
        if preference in {
            "local food",
            "food",
            "local cuisine",
            "cuisine",
        }:
            return True

        # Exact or partial food-name matching.
        if _matches_any(
            [preference],
            destination_food,
        ):
            return True

        if preference in destination_text:
            return True

    return False


# -------------------------------------------------------------------
# Location matching
# -------------------------------------------------------------------

def _location_match(
    preferences: Dict[str, Any],
    destination: Dict[str, Any],
) -> bool:
    """Check location compatibility."""

    user_location = _text(
        preferences.get("location")
    )

    if not user_location:
        return False

    destination_location = _text(
        destination.get("location")
    )

    destination_district = _text(
        destination.get("district")
    )

    destination_name = _text(
        destination.get("name")
    )

    return (
        user_location == destination_location
        or user_location == destination_district
        or user_location in destination_name
        or user_location in destination_location
        or user_location in destination_district
    )


# -------------------------------------------------------------------
# Duration matching
# -------------------------------------------------------------------

def _duration_match(
    preferences: Dict[str, Any],
    destination: Dict[str, Any],
) -> bool:
    """Check duration compatibility."""

    requested_days = preferences.get(
        "duration_days"
    )

    if requested_days is None:
        return False

    try:

        requested_days = int(
            requested_days
        )

    except (
        TypeError,
        ValueError,
    ):

        return False

    min_days = destination.get(
        "min_days"
    )

    max_days = destination.get(
        "max_days"
    )

    try:

        if min_days is not None:
            min_days = int(min_days)

        if max_days is not None:
            max_days = int(max_days)

    except (
        TypeError,
        ValueError,
    ):

        return False

    if (
        min_days is None
        and max_days is None
    ):
        return False

    if (
        min_days is not None
        and requested_days < min_days
    ):
        return False

    if (
        max_days is not None
        and requested_days > max_days
    ):
        return False

    return True


# -------------------------------------------------------------------
# Budget matching
# -------------------------------------------------------------------

def _budget_match(
    preferences: Dict[str, Any],
    destination: Dict[str, Any],
) -> bool:
    """Check budget compatibility."""

    requested_budget = preferences.get(
        "budget"
    )

    if requested_budget is None:
        return False

    destination_budget = destination.get(
        "budget"
    )

    if destination_budget is None:
        return False

    try:

        return float(
            destination_budget
        ) <= float(
            requested_budget
        )

    except (
        TypeError,
        ValueError,
    ):

        return False


# -------------------------------------------------------------------
# Weighted preference score
# -------------------------------------------------------------------

def calculate_match_score(
    preferences: Dict[str, Any],
    destination: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Calculate normalized preference score.

    Only dimensions supplied by the user
    are considered.
    """

    active_dimensions = []

    if _to_list(
        preferences.get("interests")
    ):
        active_dimensions.append(
            "interest"
        )

    if _to_list(
        preferences.get("activities")
    ):
        active_dimensions.append(
            "activity"
        )

    if _text(
        preferences.get("location")
    ):
        active_dimensions.append(
            "location"
        )

    if preferences.get(
        "duration_days"
    ) is not None:

        active_dimensions.append(
            "duration"
        )

    if preferences.get(
        "budget"
    ) is not None:

        active_dimensions.append(
            "budget"
        )

    if _to_list(
        preferences.get(
            "food_preferences"
        )
    ):
        active_dimensions.append(
            "food"
        )

    if not active_dimensions:

        return {
            "score": 0.0,
            "matching_reasons": [],
        }

    total_active_weight = sum(
        BASE_WEIGHTS[dimension]
        for dimension in active_dimensions
    )

    score = 0.0
    reasons = []

    checks = {
        "interest": _interest_match(
            preferences,
            destination,
        ),
        "activity": _activity_match(
            preferences,
            destination,
        ),
        "location": _location_match(
            preferences,
            destination,
        ),
        "duration": _duration_match(
            preferences,
            destination,
        ),
        "budget": _budget_match(
            preferences,
            destination,
        ),
        "food": _food_match(
            preferences,
            destination,
        ),
    }

    reason_text = {
        "interest": "Matches your interests",
        "activity": "Supports your requested activities",
        "location": "Matches your preferred location",
        "duration": "Fits your requested trip duration",
        "budget": "Fits your stated budget",
        "food": "Has relevant local food information",
    }

    for dimension in active_dimensions:

        if checks[dimension]:

            normalized_weight = (
                BASE_WEIGHTS[dimension]
                / total_active_weight
            )

            score += (
                normalized_weight
                * 100
            )

            reasons.append(
                reason_text[dimension]
            )

    return {
        "score": round(
            score,
            2,
        ),
        "matching_reasons": reasons,
    }


# -------------------------------------------------------------------
# Final recommendation
# -------------------------------------------------------------------

def recommend_destinations(
    preferences: Dict[str, Any],
    destinations: List[Dict[str, Any]],
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """
    Generate recommendations using:

    1. Weighted preference matching.
    2. TF-IDF content similarity.

    Final score:
        70% preference score
        30% NLP content similarity
    """

    if not destinations:
        return []

    content_scores = calculate_content_similarity(
        preferences,
        destinations,
    )

    scored_results = []

    for destination in destinations:

        preference_result = calculate_match_score(
            preferences,
            destination,
        )

        preference_score = preference_result[
            "score"
        ]

        content_score = content_scores.get(
            destination.get("name", ""),
            0.0,
        )

        final_score = (
            preference_score * 0.70
            + content_score * 0.30
        )

        if final_score <= 0:
            continue

        reasons = list(
            preference_result[
                "matching_reasons"
            ]
        )

        if content_score >= 20:

            reasons.append(
                "Tourism content is relevant to your query"
            )

        scored_results.append(
            {
                "destination": destination,
                "match_score": round(
                    final_score,
                    2,
                ),
                "matching_reasons": reasons,
                "content_similarity": round(
                    content_score,
                    2,
                ),
            }
        )

    scored_results.sort(
        key=lambda item: item[
            "match_score"
        ],
        reverse=True,
    )

    return scored_results[:limit]