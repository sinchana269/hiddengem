from math import radians, sin, cos, sqrt, atan2
from typing import Any, Dict, List, Optional
from urllib.parse import quote


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DEFAULT_VISIT_MINUTES = 90
MEAL_MINUTES = 60
TRAVEL_BUFFER_MINUTES = 15

AVERAGE_SPEED_KMPH = 30

DAY_START_MINUTES = 9 * 60
BREAKFAST_START_MINUTES = 8 * 60
LUNCH_START_MINUTES = 13 * 60
DINNER_START_MINUTES = 18 * 60


# ---------------------------------------------------------
# Distance
# ---------------------------------------------------------

def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Return straight-line distance between coordinates in km."""

    earth_radius = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return earth_radius * c


def estimate_travel_minutes(
    distance_km: float,
) -> int:
    """Estimate road travel time."""

    if distance_km <= 0:
        return 0

    return round(
        (distance_km / AVERAGE_SPEED_KMPH) * 60
    )


# ---------------------------------------------------------
# Time helpers
# ---------------------------------------------------------

def time_to_minutes(value: str) -> int:
    """Convert HH:MM to minutes from midnight."""

    hours, minutes = map(
        int,
        value.split(":"),
    )

    return hours * 60 + minutes


def minutes_to_time(value: int) -> str:
    """Convert minutes from midnight to HH:MM."""

    value = int(value)

    hours = (value // 60) % 24
    minutes = value % 60

    return f"{hours:02d}:{minutes:02d}"


# ---------------------------------------------------------
# Opening hours
# ---------------------------------------------------------

def is_open_for_visit(
    attraction: Dict[str, Any],
    start_minutes: int,
    visit_minutes: int,
) -> bool:
    """Check whether a complete visit fits inside opening hours."""

    opening = attraction.get("opening_time")
    closing = attraction.get("closing_time")

    if not opening or not closing:
        return True

    opening_minutes = time_to_minutes(opening)
    closing_minutes = time_to_minutes(closing)

    return (
        start_minutes >= opening_minutes
        and start_minutes + visit_minutes <= closing_minutes
    )


def move_to_opening_time(
    attraction: Dict[str, Any],
    current_minutes: int,
) -> int:
    """Wait until the attraction opens if necessary."""

    opening = attraction.get("opening_time")

    if not opening:
        return current_minutes

    return max(
        current_minutes,
        time_to_minutes(opening),
    )


# ---------------------------------------------------------
# Interest keywords
# ---------------------------------------------------------

HERITAGE_KEYWORDS = [
    "palace",
    "heritage",
    "historical",
    "history",
    "monument",
    "temple",
    "royal",
    "architecture",
    "fort",
]

HERITAGE_MUSEUM_KEYWORDS = [
    "museum",
    "folklore",
    "railway",
    "culture",
    "cultural",
]

NATURE_KEYWORDS = [
    "nature",
    "lake",
    "forest",
    "garden",
    "waterfall",
    "dam",
    "viewpoint",
]

WILDLIFE_KEYWORDS = [
    "wildlife",
    "sanctuary",
    "national park",
    "animal",
    "bear",
]

WATERFALL_KEYWORDS = [
    "fall",
    "waterfall",
]

PHOTOGRAPHY_KEYWORDS = [
    "viewpoint",
    "photography",
    "scenic",
    "landscape",
    "lake",
]

ADVENTURE_KEYWORDS = [
    "trek",
    "trekking",
    "rafting",
    "camping",
    "boating",
    "adventure",
]

HERITAGE_NEGATIVE_KEYWORDS = [
    "wax",
    "fantasy",
    "theme park",
    "amusement",
    "entertainment",
]


def keyword_match_score(
    text: str,
    keywords: List[str],
) -> int:
    """Count matching keywords."""

    return sum(
        1
        for keyword in keywords
        if keyword in text
    )


# ---------------------------------------------------------
# Attraction scoring
# ---------------------------------------------------------

def attraction_interest_score(
    attraction: Dict[str, Any],
    interests: List[str],
) -> int:
    """
    Calculate an internal HiddenGem relevance score.

    This is not an official tourism rating.
    """

    if not interests:
        return 0

    name = str(
        attraction.get("name") or ""
    ).lower()

    attraction_type = str(
        attraction.get("attraction_type") or ""
    ).lower()

    description = str(
        attraction.get("description") or ""
    ).lower()

    text = (
        f"{name} "
        f"{attraction_type} "
        f"{description}"
    )

    score = 0

    for raw_interest in interests:

        interest = str(
            raw_interest or ""
        ).strip().lower()

        if not interest:
            continue

        # Direct phrase match.
        if interest in text:
            score += 2

        # ---------------------------------------------
        # Heritage
        # ---------------------------------------------

        if interest == "heritage":

            score += (
                keyword_match_score(
                    text,
                    HERITAGE_KEYWORDS,
                )
                * 5
            )

            score += (
                keyword_match_score(
                    text,
                    HERITAGE_MUSEUM_KEYWORDS,
                )
                * 2
            )

            score -= (
                keyword_match_score(
                    text,
                    HERITAGE_NEGATIVE_KEYWORDS,
                )
                * 6
            )

        # ---------------------------------------------
        # Nature
        # ---------------------------------------------

        elif interest == "nature":

            score += (
                keyword_match_score(
                    text,
                    NATURE_KEYWORDS,
                )
                * 4
            )

        # ---------------------------------------------
        # Wildlife
        # ---------------------------------------------

        elif interest == "wildlife":

            score += (
                keyword_match_score(
                    text,
                    WILDLIFE_KEYWORDS,
                )
                * 5
            )

        # ---------------------------------------------
        # Waterfalls
        # ---------------------------------------------

        elif interest == "waterfalls":

            score += (
                keyword_match_score(
                    text,
                    WATERFALL_KEYWORDS,
                )
                * 5
            )

        # ---------------------------------------------
        # Photography
        # ---------------------------------------------

        elif interest == "photography":

            score += (
                keyword_match_score(
                    text,
                    PHOTOGRAPHY_KEYWORDS,
                )
                * 4
            )

        # ---------------------------------------------
        # Adventure
        # ---------------------------------------------

        elif interest == "adventure":

            score += (
                keyword_match_score(
                    text,
                    ADVENTURE_KEYWORDS,
                )
                * 4
            )

        # ---------------------------------------------
        # Temples
        # ---------------------------------------------

        elif interest == "temples":

            if "temple" in text:
                score += 8

        # ---------------------------------------------
        # Museums
        # ---------------------------------------------

        elif interest == "museums":

            if "museum" in text:
                score += 8

    return score


# ---------------------------------------------------------
# Candidate selection
# ---------------------------------------------------------

def select_attractions(
    attractions: List[Dict[str, Any]],
    interests: Optional[List[str]],
    max_stops: int,
) -> List[Dict[str, Any]]:
    """
    Select and rank attractions according to user interests.
    """

    if not attractions:
        return []

    interests = interests or []

    normalized_interests = [
        str(item).strip().lower()
        for item in interests
        if item
    ]

    if not normalized_interests:
        return attractions[:max_stops]

    scored = []

    for index, attraction in enumerate(attractions):

        score = attraction_interest_score(
            attraction,
            normalized_interests,
        )

        scored.append(
            (
                score,
                index,
                attraction,
            )
        )

    scored.sort(
        key=lambda item: (
            -item[0],
            item[1],
        )
    )

    return [
        attraction
        for _, _, attraction in scored[:max_stops]
    ]


# ---------------------------------------------------------
# Routing
# ---------------------------------------------------------

def find_nearest_attraction(
    current: Dict[str, Any],
    remaining: List[Dict[str, Any]],
):
    """Find nearest remaining attraction."""

    nearest = None
    nearest_distance = None

    for candidate in remaining:

        distance = haversine_distance(
            current["latitude"],
            current["longitude"],
            candidate["latitude"],
            candidate["longitude"],
        )

        if (
            nearest_distance is None
            or distance < nearest_distance
        ):
            nearest = candidate
            nearest_distance = distance

    return nearest, nearest_distance


# ---------------------------------------------------------
# Meals
# ---------------------------------------------------------

def add_meal(
    day_items: List[Dict[str, Any]],
    name: str,
    start_minutes: int,
) -> int:
    """Add a meal block."""

    day_items.append(
        {
            "type": "meal",
            "name": name,
            "start_time": minutes_to_time(
                start_minutes
            ),
            "end_time": minutes_to_time(
                start_minutes + MEAL_MINUTES
            ),
        }
    )

    return start_minutes + MEAL_MINUTES


def wants_local_food(
    food_preferences: Optional[List[str]],
) -> bool:
    """Check whether the traveller requested local food."""

    if not food_preferences:
        return False

    return any(
        "local" in str(item).lower()
        or "food" in str(item).lower()
        for item in food_preferences
    )


# ---------------------------------------------------------
# Main itinerary engine
# ---------------------------------------------------------

def build_itinerary(
    attractions: List[Dict[str, Any]],
    duration_days: int = 1,
    interests: Optional[List[str]] = None,
    food_preferences: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Build a practical itinerary using:

    - NLP interests
    - attraction relevance
    - coordinates
    - opening hours
    - visit duration
    - distance
    - estimated travel time
    - meal breaks

    No live routing API is required.
    """

    if not attractions:
        return {
            "days": [],
            "total_distance_km": 0,
            "total_travel_minutes": 0,
            "maps_url": None,
        }

    duration_days = max(
        1,
        duration_days or 1,
    )

    max_stops = (
        4
        if duration_days == 1
        else 5
    )

    candidates = select_attractions(
        attractions=attractions,
        interests=interests or [],
        max_stops=max_stops,
    )

    # Routing requires coordinates.
    candidates = [
        attraction
        for attraction in candidates
        if attraction.get("latitude") is not None
        and attraction.get("longitude") is not None
    ]

    if not candidates:
        return {
            "days": [],
            "total_distance_km": 0,
            "total_travel_minutes": 0,
            "maps_url": None,
        }

    local_food_requested = wants_local_food(
        food_preferences
    )

    days = []
    remaining = candidates[:]

    total_distance = 0.0
    total_travel_minutes = 0

    # -----------------------------------------------------
    # Day loop
    # -----------------------------------------------------

    for day_number in range(
        1,
        duration_days + 1,
    ):

        if not remaining:
            break

        current_time = DAY_START_MINUTES

        day_items = []

        day_distance = 0.0
        day_travel = 0

        attraction_count = 0

        # IMPORTANT:
        # These flags prevent duplicate meals.
        lunch_added = False
        dinner_added = False

        # -------------------------------------------------
        # First attraction
        # -------------------------------------------------

        current = remaining.pop(0)

        current_time = move_to_opening_time(
            current,
            current_time,
        )

        if not is_open_for_visit(
            current,
            current_time,
            DEFAULT_VISIT_MINUTES,
        ):
            continue

        start = current_time
        end = (
            start
            + DEFAULT_VISIT_MINUTES
        )

        day_items.append(
            {
                "type": "attraction",
                "name": current["name"],
                "start_time": minutes_to_time(
                    start
                ),
                "end_time": minutes_to_time(
                    end
                ),
                "distance_from_previous_km": 0,
                "travel_minutes": 0,
            }
        )

        current_time = end
        attraction_count = 1

        # -------------------------------------------------
        # Remaining attractions
        # -------------------------------------------------

        while (
            remaining
            and attraction_count < max_stops
        ):

            # ---------------------------------------------
            # Lunch
            # ---------------------------------------------

            if (
                not lunch_added
                and current_time >= LUNCH_START_MINUTES
                and attraction_count >= 2
            ):

                meal_name = (
                    "Local Food Lunch"
                    if local_food_requested
                    else "Lunch"
                )

                current_time = add_meal(
                    day_items,
                    meal_name,
                    current_time,
                )

                lunch_added = True

            # ---------------------------------------------
            # Find nearest attraction
            # ---------------------------------------------

            nearest, nearest_distance = (
                find_nearest_attraction(
                    current,
                    remaining,
                )
            )

            if nearest is None:
                break

            travel_minutes = (
                estimate_travel_minutes(
                    nearest_distance
                )
            )

            arrival_time = (
                current_time
                + travel_minutes
                + TRAVEL_BUFFER_MINUTES
            )

            arrival_time = move_to_opening_time(
                nearest,
                arrival_time,
            )

            # Skip if it cannot accommodate the visit.
            if not is_open_for_visit(
                nearest,
                arrival_time,
                DEFAULT_VISIT_MINUTES,
            ):

                remaining.remove(nearest)
                continue

            start = arrival_time
            end = (
                start
                + DEFAULT_VISIT_MINUTES
            )

            day_items.append(
                {
                    "type": "attraction",
                    "name": nearest["name"],
                    "start_time": minutes_to_time(
                        start
                    ),
                    "end_time": minutes_to_time(
                        end
                    ),
                    "distance_from_previous_km": round(
                        nearest_distance,
                        2,
                    ),
                    "travel_minutes": travel_minutes,
                }
            )

            day_distance += nearest_distance
            day_travel += travel_minutes

            current_time = end
            current = nearest

            remaining.remove(nearest)

            attraction_count += 1

            # Practical sightseeing cutoff.
            if current_time >= 17 * 60:
                break

        # -------------------------------------------------
        # Lunch fallback
        # -------------------------------------------------

        if (
            not lunch_added
            and attraction_count >= 2
            and current_time >= LUNCH_START_MINUTES
        ):

            meal_name = (
                "Local Food Lunch"
                if local_food_requested
                else "Lunch"
            )

            current_time = add_meal(
                day_items,
                meal_name,
                current_time,
            )

            lunch_added = True

        # -------------------------------------------------
        # Dinner
        # -------------------------------------------------

        if (
            not dinner_added
            and current_time < 19 * 60
            and attraction_count >= 2
        ):

            dinner_name = (
                "Local Food Dinner"
                if local_food_requested
                else "Dinner"
            )

            dinner_start = max(
                current_time,
                DINNER_START_MINUTES,
            )

            add_meal(
                day_items,
                dinner_name,
                dinner_start,
            )

            dinner_added = True

        # -------------------------------------------------
        # Store day
        # -------------------------------------------------

        days.append(
            {
                "day": day_number,
                "items": day_items,
                "distance_km": round(
                    day_distance,
                    2,
                ),
                "travel_minutes": day_travel,
            }
        )

        total_distance += day_distance
        total_travel_minutes += day_travel

    # ---------------------------------------------------------
    # Google Maps route
    # ---------------------------------------------------------

    route_points = []

    for day in days:
        for item in day["items"]:

            if item["type"] == "attraction":
                route_points.append(
                    item["name"]
                )

    maps_url = None

    if route_points:

        if len(route_points) == 1:

            maps_url = (
                "https://www.google.com/maps/search/"
                "?api=1"
                f"&query={quote(route_points[0])}"
            )

        else:

            origin = route_points[0]
            destination = route_points[-1]

            waypoints = "|".join(
                route_points[1:-1]
            )

            maps_url = (
                "https://www.google.com/maps/dir/"
                "?api=1"
                f"&origin={quote(origin)}"
                f"&destination={quote(destination)}"
            )

            if waypoints:
                maps_url += (
                    f"&waypoints={quote(waypoints)}"
                )

    # ---------------------------------------------------------
    # Final response
    # ---------------------------------------------------------

    return {
        "days": days,
        "total_distance_km": round(
            total_distance,
            2,
        ),
        "total_travel_minutes": (
            total_travel_minutes
        ),
        "maps_url": maps_url,
    }